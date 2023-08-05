//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;


var BaseGeometryModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            name: "",
            type: "BaseGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.BaseGeometry();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;

        this.property_converters['name'] = null;
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'BaseGeometryModel',

    serializers: _.extend({
    },  ThreeModel.serializers),
});

module.exports = {
    BaseGeometryModel: BaseGeometryModel,
};
