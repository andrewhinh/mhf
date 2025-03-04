import csv
import io
import json
import os
import tempfile
import uuid
from asyncio import sleep
from base64 import b64decode, b64encode
from datetime import datetime
from io import BytesIO
from pathlib import Path

import modal
import numpy as np
import requests
from dotenv import load_dotenv
from fasthtml import common as fh
from matplotlib import pyplot as plt
from PIL import Image
from simpleicons.icons import si_github
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

from utils import (
    APP_NAME,
    ARTIFACTS_PATH,
    DEFAULT_IMG_PATHS,
    MINUTES,
    PARENT_PATH,
    PYTHON_VERSION,
    SECRETS,
    VOLUME_CONFIG,
    validate_image_base64,
    validate_image_file,
)

# -----------------------------------------------------------------------------

# Modal
IMAGE = (
    modal.Image.debian_slim(python_version=PYTHON_VERSION)
    .apt_install("git")
    .run_commands(
        [
            "git clone https://github.com/Len-Stevens/Python-Antivirus.git /Python-Antivirus"
        ]
    )
    .pip_install(  # add Python dependencies
        "fastapi>=0.115.8",
        "matplotlib>=3.10.0",
        "python-fasthtml>=0.12.4",
        "simpleicons>=7.21.0",
        "starlette>=0.45.3",
        "requests>=2.32.3",
        "pillow>=10.4.0",
        "pydantic>=2.10.6",
    )
    .add_local_file(PARENT_PATH / "favicon.ico", "/root/favicon.ico")
    .add_local_dir(ARTIFACTS_PATH, "/artifacts")
)

TIMEOUT = 5 * MINUTES  # max
CONTAINER_IDLE_TIMEOUT = 15 * MINUTES  # max
ALLOW_CONCURRENT_INPUTS = 1000  # max


app = modal.App(f"{APP_NAME}-frontend")

# -----------------------------------------------------------------------------


def display_labels(g) -> str:
    plt.figure()
    image = Image.open(BytesIO(b64decode(g.input_image)))
    plt.imshow(np.array(image.convert("RGB")))
    plt.axis("off")
    response = json.loads(g.response)
    for label, points in response.items():
        width, height = image.size
        scale_x, scale_y = width / 800, height / 600
        x, y = zip(*points)
        x = [coord * scale_x for coord in x]
        y = [coord * scale_y for coord in y]
        plt.plot(x, y, "o", label=label)
    plt.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
    buf.seek(0)
    out_image_src = f"data:image/png;base64,{b64encode(buf.getvalue()).decode('utf-8')}"
    plt.close()
    return out_image_src


def get_app():  # noqa: C901
    # setup
    def before(req, sess):
        req.scope["session_id"] = sess.setdefault("session_id", str(uuid.uuid4()))

    def _not_found(req, exc):
        message = "Page not found!"
        typing_steps = len(message)
        return (
            fh.Title(APP_NAME + " | 404"),
            fh.Div(
                nav(),
                fh.Main(
                    fh.Div(
                        fh.P(
                            message,
                            hx_indicator="#spinner",
                            cls="text-2xl text-red-300 animate-typing overflow-hidden whitespace-nowrap border-r-4 border-red-300",
                            style=f"animation: typing 2s steps({typing_steps}, end), blink-caret .75s step-end infinite",
                        ),
                    ),  # to contain typing animation
                    cls="flex flex-col justify-center items-center grow gap-4 p-8",
                ),
                toast_container(),
                footer(),
                cls="flex flex-col justify-between min-h-screen text-slate-50 bg-zinc-900 w-full",
            ),
        )

    f_app, _ = fh.fast_app(
        ws_hdr=True,
        before=fh.Beforeware(
            before, skip=[r"/favicon\.ico", r"/static/.*", r".*\.css"]
        ),
        exception_handlers={404: _not_found},
        hdrs=[
            fh.Script(src="https://cdn.tailwindcss.com"),
            fh.HighlightJS(langs=["python", "javascript", "html", "css"]),
            fh.Link(rel="icon", href="/favicon.ico", type="image/x-icon"),
            fh.Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"),
            fh.Style(
                """
                @keyframes typing {
                from { width: 0; }
                to { width: 100%; }
                }
                @keyframes blink-caret {
                    from, to { border-color: transparent; }
                    50% { border-color: red; }
                }
                .htmx-swapping {
                    opacity: 0;
                    transition: opacity .25s ease-out;
                }
                """
            ),
        ],
        boost=True,
    )
    fh.setup_toasts(f_app)
    f_app.add_middleware(
        CORSMiddleware,
        allow_origins=["/"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    ## db
    db = fh.database(":memory:")
    gens = db.t.gens
    if gens not in db.t:
        gens.create(
            id=int,
            session_id=str,
            request_at=datetime,
            filename=str,
            input_image=str,  # base64
            response=str,  # json
            failed=bool,
            pk="id",
        )
    Gen = gens.dataclass()

    ## SSE state
    shutdown_event = fh.signal_shutdown()
    global shown_generations
    shown_generations = {}

    ## pagination
    max_gens = 3

    ## api/db timeout
    api_timeout = 3 * MINUTES

    ## components
    def gen_view(
        g: Gen,
        session,
    ):
        ### check if g is valid
        if not gens[g.id]:
            fh.add_toast(session, "Please refresh the page", "error")
            return None
        image_src = None
        response = validate_image_base64(g.input_image)
        if "error" in response.keys():
            fh.add_toast(session, response["error"], "error")
            return None
        image_src = f"data:image/png;base64,{g.input_image}"

        if g.failed:
            return fh.Card(
                fh.Div(
                    fh.Input(
                        type="checkbox",
                        name="selected_gens",
                        value=g.id,
                        hx_target="#gen-manage",
                        hx_swap="outerHTML",
                        hx_trigger="change",
                        hx_post="/show-select-gen-delete",
                        hx_indicator="#spinner",
                    ),
                    fh.Svg(
                        fh.NotStr(
                            """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z" /></svg>"""
                        ),
                        hx_delete=f"/gen/{g.id}",
                        hx_indicator="#spinner",
                        hx_target=f"#gen-{g.id}",
                        hx_swap="outerHTML swap:.25s",
                        hx_confirm="Are you sure?",
                        cls="w-8 h-8 text-red-300 hover:text-red-100 cursor-pointer md:block hidden border-red-300 border-2 hover:border-red-100",
                    ),
                    cls="w-1/6 flex justify-start items-center gap-2",
                ),
                fh.Div(
                    fh.Img(
                        src=image_src,
                        alt="Card image",
                        cls="max-h-48 max-w-48 md:max-h-60 md:max-w-60 object-contain",
                    ),
                    fh.P(
                        "Failed to scan image",
                        cls="text-red-300",
                    ),
                    cls="w-5/6 flex flex-col md:flex-row justify-evenly gap-4 items-center",
                ),
                cls="w-full flex justify-between items-center p-4",
                id=f"gen-{g.id}",
            )
        elif g.response:
            return fh.Card(
                fh.Div(
                    fh.Input(
                        type="checkbox",
                        name="selected_gens",
                        value=g.id,
                        hx_target="#gen-manage",
                        hx_swap="outerHTML",
                        hx_trigger="change",
                        hx_post="/show-select-gen-delete",
                        hx_indicator="#spinner",
                    ),
                    fh.Svg(
                        fh.NotStr(
                            """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z" /></svg>"""
                        ),
                        hx_delete=f"/gen/{g.id}",
                        hx_indicator="#spinner",
                        hx_target=f"#gen-{g.id}",
                        hx_swap="outerHTML swap:.25s",
                        hx_confirm="Are you sure?",
                        cls="w-8 h-8 text-red-300 hover:text-red-100 cursor-pointer md:block hidden border-red-300 border-2 hover:border-red-100",
                    ),
                    cls="w-1/6 flex justify-start items-center gap-2",
                ),
                fh.Div(
                    fh.Img(
                        src=image_src,
                        alt="Card image",
                        cls="max-h-48 max-w-48 md:max-h-60 md:max-w-60 object-contain",
                    ),
                    fh.Img(
                        src=display_labels(g),
                        alt="Card image",
                        cls="max-h-48 max-w-48 md:max-h-60 md:max-w-60 object-contain",
                    ),
                    cls="w-5/6 flex flex-col md:flex-row justify-evenly gap-4 items-center",
                ),
                cls="w-full flex justify-between items-center p-4",
                id=f"gen-{g.id}",
            )
        return fh.Card(
            fh.Div(
                fh.Input(
                    type="checkbox",
                    name="selected_gens",
                    value=g.id,
                    hx_target="#gen-manage",
                    hx_swap="outerHTML",
                    hx_trigger="change",
                    hx_post="/show-select-gen-delete",
                    hx_indicator="#spinner",
                ),
                fh.Svg(
                    fh.NotStr(
                        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z" /></svg>"""
                    ),
                    hx_delete=f"/gen/{g.id}",
                    hx_indicator="#spinner",
                    hx_target=f"#gen-{g.id}",
                    hx_swap="outerHTML swap:.25s",
                    hx_confirm="Are you sure?",
                    cls="w-8 h-8 text-red-300 hover:text-red-100 cursor-pointer md:block hidden border-red-300 border-2 hover:border-red-100",
                ),
                cls="w-1/6 flex justify-start items-center gap-2",
            ),
            fh.Div(
                fh.Img(
                    src=image_src,
                    alt="Card image",
                    cls="max-h-48 max-w-48 md:max-h-60 md:max-w-60 object-contain",
                ),
                fh.P(
                    "Loading...",
                    hx_ext="sse",
                    sse_connect=f"/stream-gens/{g.id}",
                    sse_swap="UpdateGens",
                ),
                cls="w-5/6 flex flex-col md:flex-row justify-evenly gap-4 items-center",
            ),
            cls="w-full flex justify-between items-center p-4",
            id=f"gen-{g.id}",
        )

    def num_gens(session, hx_swap_oob: bool = "false"):
        n_gens = len(gens(where=f"session_id='{session['session_id']}'"))
        return fh.Div(
            fh.P(
                f"({n_gens} total generations)",
                cls="text-blue-300 text-md whitespace-nowrap",
            ),
            id="gen-count",
            hx_swap_oob=hx_swap_oob if hx_swap_oob != "false" else None,
            cls="w-auto h-full flex justify-center items-center",
        )

    def gen_manage(session, gens_selected: bool = False, hx_swap_oob: bool = "false"):
        gens_present = len(gens(where=f"session_id='{session['session_id']}'")) > 0
        return fh.Div(
            fh.Button(
                "Delete selected",
                hx_delete="/gens/select",
                hx_indicator="#spinner",
                hx_target="#gen-list",
                hx_confirm="Are you sure?",
                cls="text-red-300 hover:text-red-100 p-2 border-red-300 border-2 hover:border-red-100 w-full h-full",
            )
            if gens_present and gens_selected
            else None,
            fh.Button(
                "Delete all",
                hx_delete="/gens",
                hx_indicator="#spinner",
                hx_target="#gen-list",
                hx_confirm="Are you sure?",
                cls="text-red-300 hover:text-red-100 p-2 border-red-300 border-2 hover:border-red-100 w-full h-full",
            )
            if gens_present
            else None,
            fh.Button(
                "Export to CSV",
                id="export-gens-csv",
                hx_get="/export-gens",
                hx_indicator="#spinner",
                hx_target="this",
                hx_swap="none",
                hx_boost="false",
                cls="text-green-300 hover:text-green-100 p-2 border-green-300 border-2 hover:border-green-100 w-full h-full",
            )
            if gens_present
            else None,
            id="gen-manage",
            hx_swap_oob=hx_swap_oob if hx_swap_oob != "false" else None,
            cls="flex flex-col md:flex-row justify-center items-center gap-4 w-full",
        )

    def gen_load_more(
        session,
        idx: int = 2,
        hx_swap_oob: str = "false",
    ):
        n_gens = len(gens(where=f"session_id='{session['session_id']}'"))
        gens_present = n_gens > 0
        still_more = n_gens > len(shown_generations)
        return fh.Div(
            fh.Button(
                "Load More",
                hx_get=f"/page-gens?idx={idx}",
                hx_indicator="#spinner",
                hx_target="#gen-list",
                hx_swap="beforeend",
                cls="text-blue-300 hover:text-blue-100 p-2 border-blue-300 border-2 hover:border-blue-100 w-full h-full",
            )
            if gens_present and still_more
            else None,
            id="load-more-gens",
            hx_swap_oob=hx_swap_oob if hx_swap_oob != "false" else None,
            cls="w-full md:w-2/3",
        )

    ## layout
    def nav():
        return fh.Nav(
            fh.A(
                f"{APP_NAME}",
                href="/",
                cls="text-xl text-blue-300 hover:text-blue-100 font-mono font-family:Consolas, Monaco, 'Lucida Console', 'Liberation Mono', 'DejaVu Sans Mono', 'Bitstream Vera Sans Mono', 'Courier New'",
            ),
            fh.Svg(
                fh.NotStr(
                    """<style>
                    .spinner_zWVm { animation: spinner_5QiW 1.2s linear infinite, spinner_PnZo 1.2s linear infinite; }
                    .spinner_gfyD { animation: spinner_5QiW 1.2s linear infinite, spinner_4j7o 1.2s linear infinite; animation-delay: .1s; }
                    .spinner_T5JJ { animation: spinner_5QiW 1.2s linear infinite, spinner_fLK4 1.2s linear infinite; animation-delay: .1s; }
                    .spinner_E3Wz { animation: spinner_5QiW 1.2s linear infinite, spinner_tDji 1.2s linear infinite; animation-delay: .2s; }
                    .spinner_g2vs { animation: spinner_5QiW 1.2s linear infinite, spinner_CMiT 1.2s linear infinite; animation-delay: .2s; }
                    .spinner_ctYB { animation: spinner_5QiW 1.2s linear infinite, spinner_cHKR 1.2s linear infinite; animation-delay: .2s; }
                    .spinner_BDNj { animation: spinner_5QiW 1.2s linear infinite, spinner_Re6e 1.2s linear infinite; animation-delay: .3s; }
                    .spinner_rCw3 { animation: spinner_5QiW 1.2s linear infinite, spinner_EJmJ 1.2s linear infinite; animation-delay: .3s; }
                    .spinner_Rszm { animation: spinner_5QiW 1.2s linear infinite, spinner_YJOP 1.2s linear infinite; animation-delay: .4s; }
                    @keyframes spinner_5QiW { 0%, 50% { width: 7.33px; height: 7.33px; } 25% { width: 1.33px; height: 1.33px; } }
                    @keyframes spinner_PnZo { 0%, 50% { x: 1px; y: 1px; } 25% { x: 4px; y: 4px; } }
                    @keyframes spinner_4j7o { 0%, 50% { x: 8.33px; y: 1px; } 25% { x: 11.33px; y: 4px; } }
                    @keyframes spinner_fLK4 { 0%, 50% { x: 1px; y: 8.33px; } 25% { x: 4px; y: 11.33px; } }
                    @keyframes spinner_tDji { 0%, 50% { x: 15.66px; y: 1px; } 25% { x: 18.66px; y: 4px; } }
                    @keyframes spinner_CMiT { 0%, 50% { x: 8.33px; y: 8.33px; } 25% { x: 11.33px; y: 11.33px; } }
                    @keyframes spinner_cHKR { 0%, 50% { x: 1px; y: 15.66px; } 25% { x: 4px; y: 18.66px; } }
                    @keyframes spinner_Re6e { 0%, 50% { x: 15.66px; y: 8.33px; } 25% { x: 18.66px; y: 11.33px; } }
                    @keyframes spinner_EJmJ { 0%, 50% { x: 8.33px; y: 15.66px; } 25% { x: 11.33px; y: 18.66px; } }
                    @keyframes spinner_YJOP { 0%, 50% { x: 15.66px; y: 15.66px; } 25% { x: 18.66px; y: 18.66px; } }
                </style>
                <rect class="spinner_zWVm" x="1" y="1" width="7.33" height="7.33"/>
                <rect class="spinner_gfyD" x="8.33" y="1" width="7.33" height="7.33"/>
                <rect class="spinner_T5JJ" x="1" y="8.33" width="7.33" height="7.33"/>
                <rect class="spinner_E3Wz" x="15.66" y="1" width="7.33" height="7.33"/>
                <rect class="spinner_g2vs" x="8.33" y="8.33" width="7.33" height="7.33"/>
                <rect class="spinner_ctYB" x="1" y="15.66" width="7.33" height="7.33"/>
                <rect class="spinner_BDNj" x="15.66" y="8.33" width="7.33" height="7.33"/>
                <rect class="spinner_rCw3" x="8.33" y="15.66" width="7.33" height="7.33"/>
                <rect class="spinner_Rszm" x="15.66" y="15.66" width="7.33" height="7.33"/>
                """
                ),
                id="spinner",
                cls="htmx-indicator w-8 h-8 absolute top-6 left-1/2 transform -translate-x-1/2 fill-blue-300",
            ),
            fh.A(
                fh.Svg(
                    fh.NotStr(
                        si_github.svg,
                    ),
                    cls="w-8 h-8 text-blue-300 hover:text-blue-100 cursor-pointer",
                ),
                href="https://github.com/andrewhinh/mhf",
                target="_blank",
            ),
            cls="flex justify-between items-center p-4 relative",
        )

    def main_content(
        session,
    ):
        curr_gens = gens(where=f"session_id='{session['session_id']}'", limit=max_gens)
        global shown_generations
        shown_generations = {}
        for g in curr_gens:
            shown_generations[g.id] = (
                "response" if g.response else "failed" if g.failed else "loading"
            )
        return fh.Main(
            fh.H1(
                "Automated Ultrasound Substructure Localization",
                cls="text-2xl font-bold text-center",
            ),
            fh.Div(
                fh.Form(
                    fh.Input(
                        id="new-image-upload",
                        name="image_file",
                        type="file",
                        accept="image/*",
                        hx_target="this",
                        hx_swap="none",
                        hx_trigger="change",
                        hx_post="/check-upload",
                        hx_indicator="#spinner",
                        hx_encoding="multipart/form-data",  # correct file encoding for check-upload since not in form
                    ),
                    fh.Button(
                        "Scan",
                        type="submit",
                        cls="text-blue-300 hover:text-blue-100 p-2 border-blue-300 border-2 hover:border-blue-100",
                    ),
                    hx_post="/upload",
                    hx_indicator="#spinner",
                    hx_target="#gen-list",
                    hx_swap="afterbegin",
                    id="gen-form",
                    cls="flex flex-col gap-4 w-full h-full",
                ),
                cls="w-full md:w-2/3 flex flex-col gap-4 justify-center items-center items-center",
            ),
            fh.Div(
                *[
                    fh.A(
                        fh.Img(
                            src=f"data:image/png;base64,{b64encode(open(img_path, 'rb').read()).decode('utf-8')}",
                            alt=f"Image {i+1}",
                            cls="w-full h-auto object-contain hover:cursor-pointer hover:opacity-100 opacity-50",
                        ),
                        href="#",
                        hx_post="/upload",
                        hx_target="#gen-list",
                        hx_swap="afterbegin",
                        hx_trigger="click",
                        hx_encoding="multipart/form-data",
                        hx_vals=json.dumps(
                            {
                                "image_path": str(img_path),
                            }
                        ),
                    )
                    for i, img_path in enumerate(DEFAULT_IMG_PATHS)
                ],
                cls="w-full md:w-2/3 grid grid-cols-2 md:grid-cols-4 gap-4",
            ),
            num_gens(session),
            fh.Form(
                gen_manage(session),
                fh.Div(
                    get_gen_table_part(session),
                    id="gen-list",
                    cls="w-full flex flex-col gap-2",
                ),
                cls="w-full md:w-2/3 flex flex-col gap-4 justify-center items-center",
            ),
            gen_load_more(
                session,
            ),
            cls="flex flex-col justify-start items-center grow gap-4 p-8",
        )

    def toast_container():
        return fh.Div(id="toast-container", cls="hidden")

    def footer():
        return fh.Footer(
            fh.Div(
                fh.P("Made by"),
                fh.A(
                    "Andrew Hinh",
                    href="https://ajhinh.com/",
                    cls="font-bold text-blue-300 hover:text-blue-100",
                ),
                cls="flex flex-col text-right gap-0.5",
            ),
            cls="flex justify-end items-center p-4 text-sm md:text-lg",
        )

    # helper fns
    @fh.threaded
    def generate_and_save(
        g: Gen,
        image_file: fh.UploadFile,
        session,
    ):
        try:
            path = ARTIFACTS_PATH / "data" / image_file.filename
            if not path.exists():  # any non-default input
                image_file.file.seek(0)  # reset pointer in case of multiple uploads
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=Path(image_file.filename).suffix
                ) as tmp_file:
                    tmp_file.write(image_file.file.read())
                    path = tmp_file.name
            response = requests.post(
                f"{os.getenv('API_URL')}",
                files={
                    "image_file": open(path, "rb"),
                },
                timeout=api_timeout,
            )
            if not response.ok:
                raise Exception(f"Failed with status code: {response.status_code}")
            g.response = response.json()
        except Exception as e:
            print(e)
            fh.add_toast(session, "Failed with error: " + str(e), "error")
            g.failed = True
        gens.update(g)

    ## SSE helpers
    async def stream_gen_updates(
        session,
        id: int,
    ):
        while not shutdown_event.is_set():
            g = gens[id]
            if g:
                curr_state = (
                    "response" if g.response else "failed" if g.failed else "loading"
                )
                global shown_generations
                if shown_generations.get(id) != curr_state:
                    shown_generations[id] = curr_state
                    yield f"""event: UpdateGens\ndata: {fh.to_xml(
                    fh.P(
                        "Loading...",
                        sse_swap="UpdateGens",
                    ) if curr_state == "loading" else
                    fh.Img(
                        src=display_labels(g),
                        alt="Card image",
                        cls="max-h-48 max-w-48 md:max-h-60 md:max-w-60 object-contain",
                    ) if curr_state == "response" else
                    fh.P(
                        "Failed to scan image",
                        cls="text-red-300",
                        sse_swap="UpdateGens",
                    ))}\n\n"""
            await sleep(1)

    ## pagination
    def get_gen_table_part(session, part_num: int = 1, size: int = max_gens):
        offset = (part_num - 1) * size
        next_gens = gens(
            where=f"session_id='{session['session_id']}'", offset=offset, limit=size
        )
        global shown_generations
        for g in next_gens:
            shown_generations[g.id] = (
                "response" if g.response else "failed" if g.failed else "loading"
            )
        paginated = [gen_view(g, session) for g in next_gens]
        return tuple(paginated)

    # routes
    ## for images, CSS, etc.
    @f_app.get("/{fname:path}.{ext:static}")
    def static_files(fname: str, ext: str):
        static_file_path = PARENT_PATH / f"{fname}.{ext}"
        if static_file_path.exists():
            return fh.FileResponse(static_file_path)

    ## toasts without target
    @f_app.post("/toast")
    def toast(session, message: str, type: str):
        fh.add_toast(session, message, type)
        return toast_container()

    ## pages
    @f_app.get("/")
    def home(
        session,
    ):
        return (
            fh.Title(APP_NAME),
            fh.Div(
                nav(),
                main_content(session),
                toast_container(),
                footer(),
                cls="flex flex-col justify-between min-h-screen text-slate-50 bg-zinc-900 w-full",
            ),
            fh.Script(
                """
                document.addEventListener('htmx:beforeRequest', (event) => {
                    if (event.target.id === 'export-gens-csv') {
                        event.preventDefault();
                        window.location.href = "/export-gens";
                    }
                });
            """
            ),
        )

    @f_app.get("/stream-gens/{id}")
    async def stream_gens(session, id: int):
        """Stream generation updates to connected clients"""
        return StreamingResponse(
            stream_gen_updates(session, id), media_type="text/event-stream"
        )

    ## input validation
    @f_app.post("/check-upload")
    def check_upload(
        session,
        image_file: fh.UploadFile,
    ):
        response = validate_image_file(image_file)
        if "error" in response.keys():
            fh.add_toast(session, response["error"], "error")
        return fh.Div(cls="hidden")

    ## pagination
    @f_app.get("/page-gens")
    def page_gens(session, idx: int):
        next_gens = get_gen_table_part(
            session, idx
        )  # separate to modify global shown_generations
        return next_gens, gen_load_more(
            session,
            idx + 1,
            "true",
        )

    ## generation routes
    @f_app.post("/upload")
    def generate_from_upload(
        session,
        image_file: fh.UploadFile = None,
        image_path: str = None,
    ):
        if not image_file and not image_path:
            fh.add_toast(session, "No image file provided", "error")
            return None
        if not image_file and image_path:
            image_file = fh.UploadFile(filename=image_path, file=open(image_path, "rb"))
        response = validate_image_file(image_file)
        if "error" in response.keys():
            fh.add_toast(session, response["error"], "error")
            return None

        # Clear input
        clear_img_input = fh.Input(
            id="new-image-upload",
            name="image_file",
            type="file",
            accept="image/*",
            hx_swap_oob="true",
        )

        # create generation for instant display, fill later
        g = Gen(
            session_id=session["session_id"],
            request_at=datetime.now(),
            filename=str(image_file.filename),
            input_image=list(response.values())[0],
            response="",
            failed=False,
        )
        g = gens.insert(g)
        global shown_generations
        shown_generations[g.id] = "loading"
        generate_and_save(g, image_file, session)
        return (
            gen_view(g, session),
            clear_img_input,
            num_gens(session, "true"),
            gen_manage(session, hx_swap_oob="true"),
            gen_load_more(
                session,
                hx_swap_oob="true",
            ),
        )

    ## delete
    @f_app.delete("/gens")
    def delete_gens(
        session,
    ):
        for gen in gens(where=f"session_id='{session['session_id']}'"):
            gens.delete(gen.id)
        global shown_generations
        shown_generations = {}
        fh.add_toast(session, "Deleted generations.", "success")
        return (
            "",
            num_gens(session, "true"),
            gen_manage(
                session,
                hx_swap_oob="true",
            ),
            gen_load_more(
                session,
                hx_swap_oob="true",
            ),
        )

    @f_app.delete("/gens/select")
    def delete_select_gens(session, selected_gens: list[int] = None):
        if selected_gens:
            for id in selected_gens:
                gens.delete(id)
            global shown_generations
            shown_generations = {
                k: v for k, v in shown_generations.items() if k not in selected_gens
            }
            fh.add_toast(session, "Deleted generations.", "success")
            remain_view = [
                gen_view(g, session)
                for g in gens(where=f"session_id='{session['session_id']}'")[::-1]
            ]
            return (
                remain_view,
                num_gens(session, "true"),
                gen_manage(
                    session,
                    hx_swap_oob="true",
                ),
                gen_load_more(
                    session,
                    hx_swap_oob="true",
                ),
            )
        else:
            return (
                gen_manage(
                    session,
                    hx_swap_oob="true",
                ),
                gen_load_more(
                    session,
                    hx_swap_oob="true",
                ),
            )

    @f_app.post("/show-select-gen-delete")
    def show_select_gen_delete(session, selected_gens: list[int] = None):
        return gen_manage(
            session,
            len(selected_gens) > 0,
        )

    @f_app.delete("/gen/{gen_id}")
    def delete_gen(
        session,
        gen_id: int,
    ):
        gens.delete(gen_id)
        global shown_generations
        shown_generations.pop(gen_id, None)
        fh.add_toast(session, "Deleted generation.", "success")
        return (
            "",
            num_gens(session, "true"),
            gen_manage(
                session,
                hx_swap_oob="true",
            ),
            gen_load_more(
                session,
                hx_swap_oob="true",
            ),
        )

    ## export to CSV
    @f_app.get("/export-gens")
    def export_gens(
        req,
    ):
        session = req.session
        if not gens(where=f"session_id='{session['session_id']}'"):
            return fh.Response(status_code=204)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "session_id",
                "request_at",
                "filename",
                "image_b64",
                "response",
                "failed",
            ]
        )
        for g in gens(where=f"session_id='{session['session_id']}'"):
            writer.writerow(
                [
                    g.session_id,
                    g.request_at,
                    g.filename,
                    g.input_image,
                    g.response,
                    g.failed,
                ]
            )

        output.seek(0)
        response = fh.Response(
            output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=gens.csv"},
        )
        return response

    return f_app


load_dotenv(PARENT_PATH / ".env")
f_app = get_app()


@app.function(
    image=IMAGE,
    volumes=VOLUME_CONFIG,
    secrets=SECRETS,
    timeout=TIMEOUT,
    container_idle_timeout=CONTAINER_IDLE_TIMEOUT,
    allow_concurrent_inputs=ALLOW_CONCURRENT_INPUTS,
)
@modal.asgi_app()
def modal_get():
    return f_app


if __name__ == "__main__":
    fh.serve(app="f_app")
