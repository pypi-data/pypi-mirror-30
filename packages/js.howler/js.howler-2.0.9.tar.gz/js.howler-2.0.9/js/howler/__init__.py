from fanstatic import Library, Resource

library = Library('howler', 'resources')

# howler.js is the combined howler.core.js and howler.spatial.js.
# If you don't need stereo or 3D positional sound, then core is all you need.
howler = Resource(
    library, 'howler.js',
    minified='howler.min.js')

howler_core = Resource(
    library, 'howler.core.js',
    minified='howler.core.min.js')

howler_spatial = Resource(
    library, 'howler.spatial.js',
    minified='howler.spatial.min.js',
    depends=[howler_core])
