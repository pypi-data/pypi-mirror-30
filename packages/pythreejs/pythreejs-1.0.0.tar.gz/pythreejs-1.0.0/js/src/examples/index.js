//
// This file auto-generated with generate-wrappers.js
//
// Load all three.js python wrappers
var loadedModules = [
    require('./.eslintrc.js'),
    require('./Detector.js'),
    require('./cameras'),
    require('./controls'),
    require('./renderers'),
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

