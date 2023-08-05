//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var LightModel = require('./Light.autogen.js').LightModel;


var RectAreaLightModel = LightModel.extend({

    defaults: function() {
        return _.extend(LightModel.prototype.defaults.call(this), {

            width: 10,
            height: 10,
            type: "RectAreaLight",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.RectAreaLight(
            this.convertColorModelToThree(this.get('color'), 'color'),
            this.convertFloatModelToThree(this.get('intensity'), 'intensity'),
            this.convertFloatModelToThree(this.get('width'), 'width'),
            this.convertFloatModelToThree(this.get('height'), 'height')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        LightModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['width'] = 'convertFloat';
        this.property_converters['height'] = 'convertFloat';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'RectAreaLightModel',

    serializers: _.extend({
    },  LightModel.serializers),
});

module.exports = {
    RectAreaLightModel: RectAreaLightModel,
};
