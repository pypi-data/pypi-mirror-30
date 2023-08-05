//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var CameraModel = require('./Camera.autogen.js').CameraModel;


var PerspectiveCameraModel = CameraModel.extend({

    defaults: function() {
        return _.extend(CameraModel.prototype.defaults.call(this), {

            fov: 50,
            zoom: 1,
            near: 0.1,
            far: 2000,
            focus: 10,
            aspect: 1,
            type: "PerspectiveCamera",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.PerspectiveCamera(
            this.convertFloatModelToThree(this.get('fov'), 'fov'),
            this.convertFloatModelToThree(this.get('aspect'), 'aspect'),
            this.convertFloatModelToThree(this.get('near'), 'near'),
            this.convertFloatModelToThree(this.get('far'), 'far')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        CameraModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['matrixWorldInverse'] = true;
        this.props_created_by_three['projectionMatrix'] = true;
        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['fov'] = 'convertFloat';
        this.property_converters['zoom'] = 'convertFloat';
        this.property_converters['near'] = 'convertFloat';
        this.property_converters['far'] = 'convertFloat';
        this.property_converters['focus'] = 'convertFloat';
        this.property_converters['aspect'] = 'convertFloat';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'PerspectiveCameraModel',

    serializers: _.extend({
    },  CameraModel.serializers),
});

module.exports = {
    PerspectiveCameraModel: PerspectiveCameraModel,
};
