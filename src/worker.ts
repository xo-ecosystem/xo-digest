export default {
  async fetch(request: Request): Promise<Response> {
    const { pathname } = new URL(request.url);
    if (pathname === "/") {
      return new Response("xo‑exchange worker up ✨", { status: 200 });
    }
    return new Response("Not Found", { status: 404 });
  },
};

