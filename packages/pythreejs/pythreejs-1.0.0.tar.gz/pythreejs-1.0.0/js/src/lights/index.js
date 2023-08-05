//
// This file auto-generated with generate-wrappers.js
//
// Load all three.js python wrappers
var loadedModules = [
    require('./AmbientLight.autogen.js'),
    require('./DirectionalLight.autogen.js'),
    require('./DirectionalLightShadow.autogen.js'),
    require('./HemisphereLight.autogen.js'),
    require('./Light.autogen.js'),
    require('./LightShadow.js'),
    require('./PointLight.autogen.js'),
    require('./RectAreaLight.autogen.js'),
    require('./SpotLight.autogen.js'),
    require('./SpotLightShadow.autogen.js'),
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

