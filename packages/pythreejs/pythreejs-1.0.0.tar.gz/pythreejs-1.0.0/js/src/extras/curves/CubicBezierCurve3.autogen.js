//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../../_base/Three.js').ThreeModel;


var CubicBezierCurve3Model = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {


        });
    },

    constructThreeObject: function() {

        var result = new THREE.CubicBezierCurve3();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);




    },

}, {

    model_name: 'CubicBezierCurve3Model',

    serializers: _.extend({
    },  ThreeModel.serializers),
});

module.exports = {
    CubicBezierCurve3Model: CubicBezierCurve3Model,
};
