//
// This file auto-generated with generate-wrappers.js
//
// Load all three.js python wrappers
var loadedModules = [
    require('./AnimationLoader.autogen.js'),
    require('./AudioLoader.autogen.js'),
    require('./BufferGeometryLoader.autogen.js'),
    require('./Cache.autogen.js'),
    require('./CompressedTextureLoader.autogen.js'),
    require('./CubeTextureLoader.autogen.js'),
    require('./DataTextureLoader.autogen.js'),
    require('./FileLoader.autogen.js'),
    require('./FontLoader.autogen.js'),
    require('./ImageBitmapLoader.autogen.js'),
    require('./ImageLoader.autogen.js'),
    require('./JSONLoader.autogen.js'),
    require('./Loader.autogen.js'),
    require('./LoadingManager.autogen.js'),
    require('./MaterialLoader.autogen.js'),
    require('./ObjectLoader.autogen.js'),
    require('./TextureLoader.autogen.js'),
];

for (var i in loadedModules) {
    if (loadedModules.hasOwnProperty(i)) {
        var loadedModule = loadedModules[i];
        for (var target_name in loadedModule) {
            if (loadedModule.hasOwnProperty(target_name)) {
                module.exports[target_name] = loadedModule[target_name];
            }
        }
    }
}

