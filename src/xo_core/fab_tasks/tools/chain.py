

from invoke import Collection

ns = Collection("tools")

# Add tools submodules that have ns collections
try:
    from . import cursor
    ns.add_collection(cursor.ns, name="cursor")
except ImportError:
    pass

try:
    from . import describe
    ns.add_collection(describe.ns, name="describe")
except ImportError:
    pass

try:
    from . import doctor
    ns.add_collection(doctor.ns, name="doctor")
except ImportError:
    pass

try:
    from . import lint
    ns.add_collection(lint.ns, name="lint")
except ImportError:
    pass

try:
    from . import meta_generate
    ns.add_collection(meta_generate.ns, name="meta-generate")
except ImportError:
    pass

try:
    from . import open
    ns.add_collection(open.ns, name="open")
except ImportError:
    pass

try:
    from . import pulse
    ns.add_collection(pulse.ns, name="pulse")
except ImportError:
    pass

try:
    from . import foo
    ns.add_collection(foo.ns, name="foo")
except ImportError:
    pass