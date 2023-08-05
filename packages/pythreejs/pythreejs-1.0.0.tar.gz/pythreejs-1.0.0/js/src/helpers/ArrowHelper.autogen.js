//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var Object3DModel = require('../core/Object3D.js').Object3DModel;


var ArrowHelperModel = Object3DModel.extend({

    defaults: function() {
        return _.extend(Object3DModel.prototype.defaults.call(this), {

            dir: [1,0,0],
            origin: [0,0,0],
            length: 1,
            hex: 0,
            headLength: null,
            headWidth: null,
            type: "ArrowHelper",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.ArrowHelper();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        Object3DModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['dir'] = 'convertVector';
        this.property_converters['origin'] = 'convertVector';
        this.property_converters['length'] = 'convertFloat';
        this.property_converters['hex'] = null;
        this.property_converters['headLength'] = 'convertFloat';
        this.property_converters['headWidth'] = 'convertFloat';
        this.property_converters['type'] = null;

        this.property_assigners['dir'] = 'assignVector';
        this.property_assigners['origin'] = 'assignVector';

    },

}, {

    model_name: 'ArrowHelperModel',

    serializers: _.extend({
    },  Object3DModel.serializers),
});

module.exports = {
    ArrowHelperModel: ArrowHelperModel,
};
