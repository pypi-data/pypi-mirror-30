//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;


var FogModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            name: "",
            color: "white",
            near: 1,
            far: 1000,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Fog(
            this.convertColorModelToThree(this.get('color'), 'color'),
            this.convertFloatModelToThree(this.get('near'), 'near'),
            this.convertFloatModelToThree(this.get('far'), 'far')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);


        this.property_converters['name'] = null;
        this.property_converters['color'] = 'convertColor';
        this.property_converters['near'] = 'convertFloat';
        this.property_converters['far'] = 'convertFloat';


    },

}, {

    model_name: 'FogModel',

    serializers: _.extend({
    },  ThreeModel.serializers),
});

module.exports = {
    FogModel: FogModel,
};
