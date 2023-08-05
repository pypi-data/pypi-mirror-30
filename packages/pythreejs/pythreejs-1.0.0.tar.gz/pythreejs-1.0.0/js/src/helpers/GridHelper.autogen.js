//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var Object3DModel = require('../core/Object3D.js').Object3DModel;


var GridHelperModel = Object3DModel.extend({

    defaults: function() {
        return _.extend(Object3DModel.prototype.defaults.call(this), {

            size: 10,
            divisions: 10,
            colorCenterLine: "0x444444",
            colorGrid: "0x888888",
            type: "GridHelper",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.GridHelper(
            this.convertFloatModelToThree(this.get('size'), 'size'),
            this.get('divisions'),
            this.convertColorModelToThree(this.get('colorCenterLine'), 'colorCenterLine'),
            this.convertColorModelToThree(this.get('colorGrid'), 'colorGrid')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        Object3DModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['size'] = 'convertFloat';
        this.property_converters['divisions'] = null;
        this.property_converters['colorCenterLine'] = 'convertColor';
        this.property_converters['colorGrid'] = 'convertColor';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'GridHelperModel',

    serializers: _.extend({
    },  Object3DModel.serializers),
});

module.exports = {
    GridHelperModel: GridHelperModel,
};
