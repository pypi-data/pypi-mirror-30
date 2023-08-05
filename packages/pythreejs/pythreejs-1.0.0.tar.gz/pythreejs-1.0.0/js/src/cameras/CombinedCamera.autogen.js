//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var CameraModel = require('./Camera.autogen.js').CameraModel;


var CombinedCameraModel = CameraModel.extend({

    defaults: function() {
        return _.extend(CameraModel.prototype.defaults.call(this), {

            fov: 50,
            zoom: 1,
            near: 0.1,
            far: 2000,
            orthoNear: 0.1,
            orthoFar: 2000,
            width: 0,
            height: 0,
            mode: "perspective",
            impersonate: true,
            type: "CombinedCamera",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.CombinedCamera(
            this.convertFloatModelToThree(this.get('width'), 'width'),
            this.convertFloatModelToThree(this.get('height'), 'height'),
            this.convertFloatModelToThree(this.get('fov'), 'fov'),
            this.convertFloatModelToThree(this.get('near'), 'near'),
            this.convertFloatModelToThree(this.get('far'), 'far'),
            this.convertFloatModelToThree(this.get('orthoNear'), 'orthoNear'),
            this.convertFloatModelToThree(this.get('orthoFar'), 'orthoFar')
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
        this.enum_property_types['mode'] = '[&#x27;perspective&#x27;, &#x27;orthographic&#x27;]';

        this.property_converters['fov'] = 'convertFloat';
        this.property_converters['zoom'] = 'convertFloat';
        this.property_converters['near'] = 'convertFloat';
        this.property_converters['far'] = 'convertFloat';
        this.property_converters['orthoNear'] = 'convertFloat';
        this.property_converters['orthoFar'] = 'convertFloat';
        this.property_converters['width'] = 'convertFloat';
        this.property_converters['height'] = 'convertFloat';
        this.property_converters['mode'] = 'convertEnum';
        this.property_converters['impersonate'] = 'convertBool';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'CombinedCameraModel',

    serializers: _.extend({
    },  CameraModel.serializers),
});

module.exports = {
    CombinedCameraModel: CombinedCameraModel,
};
