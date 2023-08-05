//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var Object3DModel = require('../core/Object3D.js').Object3DModel;


var AxesHelperModel = Object3DModel.extend({

    defaults: function() {
        return _.extend(Object3DModel.prototype.defaults.call(this), {

            size: 1,
            type: "AxesHelper",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.AxesHelper(
            this.convertFloatModelToThree(this.get('size'), 'size')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        Object3DModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['size'] = 'convertFloat';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'AxesHelperModel',

    serializers: _.extend({
    },  Object3DModel.serializers),
});

module.exports = {
    AxesHelperModel: AxesHelperModel,
};
