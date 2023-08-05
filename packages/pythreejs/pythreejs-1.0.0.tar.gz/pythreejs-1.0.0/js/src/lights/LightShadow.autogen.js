//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;

var CameraModel = require('../cameras/Camera.autogen.js').CameraModel;

var LightShadowModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            camera: 'uninitialized',
            bias: 0,
            mapSize: [512,512],
            radius: 1,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.LightShadow(
            this.convertThreeTypeModelToThree(this.get('camera'), 'camera')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('camera');


        this.property_converters['camera'] = 'convertThreeType';
        this.property_converters['bias'] = 'convertFloat';
        this.property_converters['mapSize'] = 'convertVector';
        this.property_converters['radius'] = 'convertFloat';

        this.property_assigners['mapSize'] = 'assignVector';

    },

}, {

    model_name: 'LightShadowModel',

    serializers: _.extend({
        camera: { deserialize: widgets.unpack_models },
    },  ThreeModel.serializers),
});

module.exports = {
    LightShadowModel: LightShadowModel,
};
