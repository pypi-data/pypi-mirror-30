//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var Object3DModel = require('../core/Object3D.js').Object3DModel;


var CameraModel = Object3DModel.extend({

    defaults: function() {
        return _.extend(Object3DModel.prototype.defaults.call(this), {

            matrixWorldInverse: [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
            projectionMatrix: [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
            type: "Camera",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Camera();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        Object3DModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['matrixWorldInverse'] = true;
        this.props_created_by_three['projectionMatrix'] = true;
        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['matrixWorldInverse'] = 'convertMatrix';
        this.property_converters['projectionMatrix'] = 'convertMatrix';
        this.property_converters['type'] = null;

        this.property_assigners['matrixWorldInverse'] = 'assignMatrix';
        this.property_assigners['projectionMatrix'] = 'assignMatrix';

    },

}, {

    model_name: 'CameraModel',

    serializers: _.extend({
    },  Object3DModel.serializers),
});

module.exports = {
    CameraModel: CameraModel,
};
