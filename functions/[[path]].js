import { getAssetFromKV } from "@cloudflare/kv-asset-handler";
addEventListener('fetch', event => {
    event.respondWith(getAssetFromKV(event))
})
async function handleEvent(event) {
    try {
        return await getAssetFromKV(event)
    } catch (e) {
        try {
            let response = await fetch('${process.env.PROCESS_URL}${new URL(event.request.url).pathname}')
            if (response.status === 404) {
                return new Response('Not Found', { status: 404 })
            }
            return response
        } catch (error) {
            return new Response('Internal Server Error', { status: 500 })
        }
    }
}
