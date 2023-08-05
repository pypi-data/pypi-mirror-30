//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseGeometryModel = require('../core/BaseGeometry.autogen.js').BaseGeometryModel;


var ParametricGeometryModel = BaseGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseGeometryModel.prototype.defaults.call(this), {

            func: function (u,v) { return THREE.Vector3(); },
            slices: 3,
            stacks: 3,
            type: "ParametricGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.ParametricGeometry(
            this.convertFunctionModelToThree(this.get('func'), 'func'),
            this.get('slices'),
            this.get('stacks')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        BaseGeometryModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;

        this.property_converters['func'] = 'convertFunction';
        this.property_converters['slices'] = null;
        this.property_converters['stacks'] = null;
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'ParametricGeometryModel',

    serializers: _.extend({
    },  BaseGeometryModel.serializers),
});

module.exports = {
    ParametricGeometryModel: ParametricGeometryModel,
};
