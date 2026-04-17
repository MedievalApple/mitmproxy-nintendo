from mitmproxy import http, ctx
import mitmproxy.http

class PretendoAddon:
    def load(self, loader) -> None:
        loader.add_option(
            name="badge_arcade_redirect",
            typespec=bool,
            default=False,
            help="Redirect Badge Arcade rquests to custom server",
        )

        loader.add_option(
            name="badge_arcade_host",
            typespec=str,
            default="",
            help="Host to send Badge Arcade requests to (keeps the original host in the Host header)",
        )

        loader.add_option(
            name="badge_arcade_host_port",
            typespec=int,
            default=59400,
            help="Port to send Badge Arcade requests to (only applies if badge_arcade_host is set)",
        )

        loader.add_option(
            name="pretendo_redirect",
            typespec=bool,
            default=False,
            help="Redirect all requests from Nintendo to Pretendo",
        )

        loader.add_option(
            name="pretendo_host",
            typespec=str,
            default="",
            help="Host to send Pretendo requests to (keeps the original host in the Host header)",
        )

        loader.add_option(
            name="pretendo_host_port",
            typespec=int,
            default=80,
            help="Port to send Pretendo requests to (only applies if pretendo_host is set)",
        )

        loader.add_option(
            name="pretendo_http",
            typespec=bool,
            default=False,
            help="Sets Pretendo requests to HTTP (only applies if pretendo_host is set)",
        )

    def request(self, flow: http.HTTPFlow) -> None:
        if ctx.options.pretendo_redirect:
            if "nintendo.net" in flow.request.pretty_host:
                flow.request.host = flow.request.pretty_host.replace(
                    "nintendo.net", "pretendo.cc"
                )
            elif "nintendowifi.net" in flow.request.pretty_host:
                flow.request.host = flow.request.pretty_host.replace(
                    "nintendowifi.net", "pretendo.cc"
                )

            if ctx.options.pretendo_host and (
                "pretendo.cc" in flow.request.pretty_host
                or "pretendo.network" in flow.request.pretty_host
                or "pretendo-cdn.b-cdn.net" in flow.request.pretty_host
            ):
                original_host = flow.request.host_header
                flow.request.host = ctx.options.pretendo_host
                flow.request.port = ctx.options.pretendo_host_port
                flow.request.host_header = original_host

                if ctx.options.pretendo_http:
                    flow.request.scheme = "http"

        if ctx.options.badge_arcade_redirect and (
            flow.request.pretty_url == "https://account.pretendo.cc/v1/api/provider/nex_token/@me?game_server_id=00134600"
        ):
            flow.response = mitmproxy.http.Response.make(
                200,
                f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><nex_token><host>{ctx.options.badge_arcade_host}</host><nex_password>nexpassword</nex_password><pid>PID</pid><port>{ctx.options.badge_arcade_host_port}</port><token>token</token></nex_token>''',
                {"Content-Type":"application/xml;charset=UTF-8"}
            )


addons = [PretendoAddon()]
