//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var MaterialModel = require('./Material.js').MaterialModel;


var LineDashedMaterialModel = MaterialModel.extend({

    defaults: function() {
        return _.extend(MaterialModel.prototype.defaults.call(this), {

            color: "#ffffff",
            lights: false,
            linewidth: 1,
            scale: 1,
            dashSize: 3,
            gapSize: 1,
            type: "LineDashedMaterial",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.LineDashedMaterial(
            {
                color: this.convertColorModelToThree(this.get('color'), 'color'),
                lights: this.convertBoolModelToThree(this.get('lights'), 'lights'),
                linewidth: this.convertFloatModelToThree(this.get('linewidth'), 'linewidth'),
                scale: this.convertFloatModelToThree(this.get('scale'), 'scale'),
                dashSize: this.convertFloatModelToThree(this.get('dashSize'), 'dashSize'),
                gapSize: this.convertFloatModelToThree(this.get('gapSize'), 'gapSize'),
                type: this.get('type'),
            }
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        MaterialModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;

        this.property_converters['color'] = 'convertColor';
        this.property_converters['lights'] = 'convertBool';
        this.property_converters['linewidth'] = 'convertFloat';
        this.property_converters['scale'] = 'convertFloat';
        this.property_converters['dashSize'] = 'convertFloat';
        this.property_converters['gapSize'] = 'convertFloat';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'LineDashedMaterialModel',

    serializers: _.extend({
    },  MaterialModel.serializers),
});

module.exports = {
    LineDashedMaterialModel: LineDashedMaterialModel,
};
