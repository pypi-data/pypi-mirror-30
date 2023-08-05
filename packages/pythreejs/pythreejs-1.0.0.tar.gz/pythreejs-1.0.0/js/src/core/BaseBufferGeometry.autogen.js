//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;


var BaseBufferGeometryModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            name: "",
            type: "BaseBufferGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.BaseBufferGeometry();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;

        this.property_converters['name'] = null;
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'BaseBufferGeometryModel',

    serializers: _.extend({
    },  ThreeModel.serializers),
});

module.exports = {
    BaseBufferGeometryModel: BaseBufferGeometryModel,
};
