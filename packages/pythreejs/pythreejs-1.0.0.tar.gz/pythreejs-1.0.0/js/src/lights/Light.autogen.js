//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var Object3DModel = require('../core/Object3D.js').Object3DModel;


var LightModel = Object3DModel.extend({

    defaults: function() {
        return _.extend(Object3DModel.prototype.defaults.call(this), {

            color: "#ffffff",
            intensity: 1,
            type: "Light",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Light(
            this.convertColorModelToThree(this.get('color'), 'color'),
            this.convertFloatModelToThree(this.get('intensity'), 'intensity')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        Object3DModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['color'] = 'convertColor';
        this.property_converters['intensity'] = 'convertFloat';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'LightModel',

    serializers: _.extend({
    },  Object3DModel.serializers),
});

module.exports = {
    LightModel: LightModel,
};
