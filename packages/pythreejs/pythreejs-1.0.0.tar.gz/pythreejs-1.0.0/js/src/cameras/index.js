//
// This file auto-generated with generate-wrappers.js
//
// Load all three.js python wrappers
var loadedModules = [
    require('./ArrayCamera.autogen.js'),
    require('./Camera.autogen.js'),
    require('./CombinedCamera.js'),
    require('./CubeCamera.autogen.js'),
    require('./OrthographicCamera.js'),
    require('./PerspectiveCamera.js'),
    require('./StereoCamera.autogen.js'),
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

