//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var LightModel = require('./Light.autogen.js').LightModel;


var HemisphereLightModel = LightModel.extend({

    defaults: function() {
        return _.extend(LightModel.prototype.defaults.call(this), {

            groundColor: "#000000",
            type: "HemisphereLight",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.HemisphereLight(
            this.convertColorModelToThree(this.get('color'), 'color'),
            this.convertColorModelToThree(this.get('groundColor'), 'groundColor'),
            this.convertFloatModelToThree(this.get('intensity'), 'intensity')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        LightModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['groundColor'] = 'convertColor';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'HemisphereLightModel',

    serializers: _.extend({
    },  LightModel.serializers),
});

module.exports = {
    HemisphereLightModel: HemisphereLightModel,
};
