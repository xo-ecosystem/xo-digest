from invoke import Collection

from xo_core.fab_tasks.pulse import (
    auto,
    archive,
    delete,
    dev,
    new,
    preview,
    publish,
    review,
    sign,
    sync,
    test,
    thirdweb_mint,
    pulse,
    pin_to_arweave,
    export_html,
)

ns = Collection("pulse")
ns.add_collection(auto.ns, name="auto")
ns.add_collection(archive.ns, name="archive")
ns.add_collection(delete.ns, name="delete")
ns.add_collection(dev.ns, name="dev")
ns.add_collection(new.ns, name="new")
ns.add_collection(preview.ns, name="preview")
ns.add_collection(publish.ns, name="publish")
ns.add_collection(review.ns, name="review")
ns.add_collection(sign.ns, name="sign")
ns.add_collection(sync.ns, name="sync")
ns.add_collection(test.ns, name="test")
ns.add_collection(thirdweb_mint.ns, name="thirdweb-mint")
ns.add_collection(pulse.ns, name="pulse")
ns.add_collection(pin_to_arweave.ns, name="pin-to-arweave")
ns.add_collection(export_html.ns, name="export-html")