//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var Object3DModel = require('../core/Object3D.js').Object3DModel;

var CameraModel = require('../cameras/Camera.autogen.js').CameraModel;

var CameraHelperModel = Object3DModel.extend({

    defaults: function() {
        return _.extend(Object3DModel.prototype.defaults.call(this), {

            camera: null,
            type: "CameraHelper",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.CameraHelper(
            this.convertThreeTypeModelToThree(this.get('camera'), 'camera')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        Object3DModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('camera');

        this.props_created_by_three['matrixAutoUpdate'] = true;
        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['camera'] = 'convertThreeType';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'CameraHelperModel',

    serializers: _.extend({
        camera: { deserialize: widgets.unpack_models },
    },  Object3DModel.serializers),
});

module.exports = {
    CameraHelperModel: CameraHelperModel,
};
