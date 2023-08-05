//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var Object3DModel = require('../core/Object3D.js').Object3DModel;

var HemisphereLightModel = require('../lights/HemisphereLight.autogen.js').HemisphereLightModel;

var HemisphereLightHelperModel = Object3DModel.extend({

    defaults: function() {
        return _.extend(Object3DModel.prototype.defaults.call(this), {

            light: null,
            size: 1,
            color: "#ffffff",
            type: "HemisphereLightHelper",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.HemisphereLightHelper(
            this.convertThreeTypeModelToThree(this.get('light'), 'light'),
            this.convertFloatModelToThree(this.get('size'), 'size'),
            this.convertColorModelToThree(this.get('color'), 'color')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        Object3DModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('light');

        this.props_created_by_three['matrixAutoUpdate'] = true;
        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['light'] = 'convertThreeType';
        this.property_converters['size'] = 'convertFloat';
        this.property_converters['color'] = 'convertColor';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'HemisphereLightHelperModel',

    serializers: _.extend({
        light: { deserialize: widgets.unpack_models },
    },  Object3DModel.serializers),
});

module.exports = {
    HemisphereLightHelperModel: HemisphereLightHelperModel,
};
