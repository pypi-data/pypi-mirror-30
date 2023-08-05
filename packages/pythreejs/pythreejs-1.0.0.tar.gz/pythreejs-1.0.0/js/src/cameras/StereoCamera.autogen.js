//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;

var PerspectiveCameraModel = require('./PerspectiveCamera.js').PerspectiveCameraModel;

var StereoCameraModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            aspect: 1,
            eyeSep: 0.064,
            cameraL: null,
            cameraR: null,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.StereoCamera();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('cameraL');
        this.three_properties.push('cameraR');


        this.property_converters['aspect'] = 'convertFloat';
        this.property_converters['eyeSep'] = 'convertFloat';
        this.property_converters['cameraL'] = 'convertThreeType';
        this.property_converters['cameraR'] = 'convertThreeType';


    },

}, {

    model_name: 'StereoCameraModel',

    serializers: _.extend({
        cameraL: { deserialize: widgets.unpack_models },
        cameraR: { deserialize: widgets.unpack_models },
    },  ThreeModel.serializers),
});

module.exports = {
    StereoCameraModel: StereoCameraModel,
};
