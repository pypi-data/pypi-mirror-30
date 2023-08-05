//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var CameraModel = require('./Camera.autogen.js').CameraModel;


var OrthographicCameraModel = CameraModel.extend({

    defaults: function() {
        return _.extend(CameraModel.prototype.defaults.call(this), {

            zoom: 1,
            left: 0,
            right: 0,
            top: 0,
            bottom: 0,
            near: 0.1,
            far: 2000,
            type: "OrthographicCamera",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.OrthographicCamera(
            this.convertFloatModelToThree(this.get('left'), 'left'),
            this.convertFloatModelToThree(this.get('right'), 'right'),
            this.convertFloatModelToThree(this.get('top'), 'top'),
            this.convertFloatModelToThree(this.get('bottom'), 'bottom'),
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

        this.property_converters['zoom'] = 'convertFloat';
        this.property_converters['left'] = 'convertFloat';
        this.property_converters['right'] = 'convertFloat';
        this.property_converters['top'] = 'convertFloat';
        this.property_converters['bottom'] = 'convertFloat';
        this.property_converters['near'] = 'convertFloat';
        this.property_converters['far'] = 'convertFloat';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'OrthographicCameraModel',

    serializers: _.extend({
    },  CameraModel.serializers),
});

module.exports = {
    OrthographicCameraModel: OrthographicCameraModel,
};
