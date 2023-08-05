//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var Object3DModel = require('../core/Object3D.js').Object3DModel;


var PolarGridHelperModel = Object3DModel.extend({

    defaults: function() {
        return _.extend(Object3DModel.prototype.defaults.call(this), {

            radius: 10,
            radials: 16,
            circles: 8,
            divisions: 64,
            color1: "0x444444",
            color2: "0x888888",
            type: "PolarGridHelper",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.PolarGridHelper(
            this.get('radius'),
            this.get('radials'),
            this.get('circles'),
            this.get('divisions'),
            this.convertColorModelToThree(this.get('color1'), 'color1'),
            this.convertColorModelToThree(this.get('color2'), 'color2')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        Object3DModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['radius'] = null;
        this.property_converters['radials'] = null;
        this.property_converters['circles'] = null;
        this.property_converters['divisions'] = null;
        this.property_converters['color1'] = 'convertColor';
        this.property_converters['color2'] = 'convertColor';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'PolarGridHelperModel',

    serializers: _.extend({
    },  Object3DModel.serializers),
});

module.exports = {
    PolarGridHelperModel: PolarGridHelperModel,
};
