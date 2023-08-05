//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;


var FogExp2Model = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            name: "",
            color: "white",
            density: 0.00025,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.FogExp2(
            this.convertColorModelToThree(this.get('color'), 'color'),
            this.convertFloatModelToThree(this.get('density'), 'density')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);


        this.property_converters['name'] = null;
        this.property_converters['color'] = 'convertColor';
        this.property_converters['density'] = 'convertFloat';


    },

}, {

    model_name: 'FogExp2Model',

    serializers: _.extend({
    },  ThreeModel.serializers),
});

module.exports = {
    FogExp2Model: FogExp2Model,
};
