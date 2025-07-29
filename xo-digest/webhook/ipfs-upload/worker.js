export async function uploadToIPFS({ filename, content, markdown = false, token }) {
  const mimeType = markdown ? "text/markdown" : "text/plain";
  const file = new File([content], filename, { type: mimeType });

  const client = new NFTStorage({ token });
  const cid = await client.storeBlob(file);
  return {
    cid,
    url: `https://ipfs.io/ipfs/${cid}`,
    filename
  };
}

import { NFTStorage, File } from 'nft.storage'

const NFT_STORAGE_TOKEN = "YOUR_NFT_STORAGE_API_KEY"; // Consider using env.NFT_STORAGE_TOKEN

export default {
  async fetch(request, env, ctx) {
    if (request.method !== "POST") {
      return new Response("Only POST requests allowed", { status: 405 });
    }

    try {
      const contentType = request.headers.get("Content-Type") || "";
      if (!contentType.includes("application/json")) {
        return new Response("Expected JSON payload", { status: 400 });
      }

      const payload = await request.json();
      const { filename, content, markdown } = payload;

      if (!filename || !content) {
        return new Response("Missing required fields: filename or content", { status: 400 });
      }

      const { cid, url } = await uploadToIPFS({
        filename,
        content,
        markdown,
        token: env.NFT_STORAGE_TOKEN || NFT_STORAGE_TOKEN
      });

      return Response.json({
        status: "success",
        message: "File uploaded to IPFS",
        url,
        cid,
        filename,
      });

    } catch (err) {
      return new Response(`Error: ${err.message}`, { status: 500 });
    }
  },
};