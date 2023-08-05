//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var LightModel = require('./Light.autogen.js').LightModel;

var Object3DModel = require('../core/Object3D.js').Object3DModel;
var LightShadowModel = require('./LightShadow.js').LightShadowModel;

var SpotLightModel = LightModel.extend({

    defaults: function() {
        return _.extend(LightModel.prototype.defaults.call(this), {

            target: 'uninitialized',
            distance: 0,
            angle: 1.0471975511965976,
            penumbra: 0,
            decay: 1,
            shadow: 'uninitialized',
            type: "SpotLight",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.SpotLight(
            this.convertColorModelToThree(this.get('color'), 'color'),
            this.convertFloatModelToThree(this.get('intensity'), 'intensity'),
            this.convertFloatModelToThree(this.get('distance'), 'distance'),
            this.convertFloatModelToThree(this.get('angle'), 'angle'),
            this.convertFloatModelToThree(this.get('penumbra'), 'penumbra'),
            this.convertFloatModelToThree(this.get('decay'), 'decay')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        LightModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('target');
        this.three_properties.push('shadow');

        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['target'] = 'convertThreeType';
        this.property_converters['distance'] = 'convertFloat';
        this.property_converters['angle'] = 'convertFloat';
        this.property_converters['penumbra'] = 'convertFloat';
        this.property_converters['decay'] = 'convertFloat';
        this.property_converters['shadow'] = 'convertThreeType';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'SpotLightModel',

    serializers: _.extend({
        target: { deserialize: widgets.unpack_models },
        shadow: { deserialize: widgets.unpack_models },
    },  LightModel.serializers),
});

module.exports = {
    SpotLightModel: SpotLightModel,
};
