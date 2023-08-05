//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseGeometryModel = require('../core/BaseGeometry.autogen.js').BaseGeometryModel;


var TextGeometryModel = BaseGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseGeometryModel.prototype.defaults.call(this), {

            type: "TextGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.TextGeometry();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        BaseGeometryModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;

        this.property_converters['type'] = null;


    },

}, {

    model_name: 'TextGeometryModel',

    serializers: _.extend({
    },  BaseGeometryModel.serializers),
});

module.exports = {
    TextGeometryModel: TextGeometryModel,
};
