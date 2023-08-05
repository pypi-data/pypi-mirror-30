//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var LightModel = require('./Light.autogen.js').LightModel;

var LightShadowModel = require('./LightShadow.js').LightShadowModel;

var PointLightModel = LightModel.extend({

    defaults: function() {
        return _.extend(LightModel.prototype.defaults.call(this), {

            power: 12.566370614359172,
            distance: 0,
            decay: 1,
            shadow: 'uninitialized',
            type: "PointLight",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.PointLight(
            this.convertColorModelToThree(this.get('color'), 'color'),
            this.convertFloatModelToThree(this.get('intensity'), 'intensity'),
            this.convertFloatModelToThree(this.get('distance'), 'distance'),
            this.convertFloatModelToThree(this.get('decay'), 'decay')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        LightModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('shadow');

        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['power'] = 'convertFloat';
        this.property_converters['distance'] = 'convertFloat';
        this.property_converters['decay'] = 'convertFloat';
        this.property_converters['shadow'] = 'convertThreeType';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'PointLightModel',

    serializers: _.extend({
        shadow: { deserialize: widgets.unpack_models },
    },  LightModel.serializers),
});

module.exports = {
    PointLightModel: PointLightModel,
};
