//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;


var Object3DModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            name: "",
            type: "Object3D",
            children: [],
            up: [0,1,0],
            position: [0,0,0],
            rotation: [0,0,0,"XYZ"],
            quaternion: [0,0,0,1],
            scale: [1,1,1],
            modelViewMatrix: [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
            normalMatrix: [1,0,0,0,1,0,0,0,1],
            matrix: [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
            matrixWorld: [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
            matrixAutoUpdate: true,
            matrixWorldNeedsUpdate: false,
            visible: true,
            castShadow: false,
            receiveShadow: false,
            frustumCulled: true,
            renderOrder: 0,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Object3D();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);
        this.three_nested_properties.push('children');

        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['name'] = null;
        this.property_converters['type'] = null;
        this.property_converters['children'] = 'convertThreeTypeArray';
        this.property_converters['up'] = 'convertVector';
        this.property_converters['position'] = 'convertVector';
        this.property_converters['rotation'] = 'convertEuler';
        this.property_converters['quaternion'] = 'convertVector';
        this.property_converters['scale'] = 'convertVector';
        this.property_converters['modelViewMatrix'] = 'convertMatrix';
        this.property_converters['normalMatrix'] = 'convertMatrix';
        this.property_converters['matrix'] = 'convertMatrix';
        this.property_converters['matrixWorld'] = 'convertMatrix';
        this.property_converters['matrixAutoUpdate'] = 'convertBool';
        this.property_converters['matrixWorldNeedsUpdate'] = 'convertBool';
        this.property_converters['visible'] = 'convertBool';
        this.property_converters['castShadow'] = 'convertBool';
        this.property_converters['receiveShadow'] = 'convertBool';
        this.property_converters['frustumCulled'] = 'convertBool';
        this.property_converters['renderOrder'] = null;

        this.property_assigners['up'] = 'assignVector';
        this.property_assigners['position'] = 'assignVector';
        this.property_assigners['rotation'] = 'assignEuler';
        this.property_assigners['quaternion'] = 'assignVector';
        this.property_assigners['scale'] = 'assignVector';
        this.property_assigners['modelViewMatrix'] = 'assignMatrix';
        this.property_assigners['normalMatrix'] = 'assignMatrix';
        this.property_assigners['matrix'] = 'assignMatrix';
        this.property_assigners['matrixWorld'] = 'assignMatrix';

    },

}, {

    model_name: 'Object3DModel',

    serializers: _.extend({
        children: { deserialize: widgets.unpack_models },
    },  ThreeModel.serializers),
});

module.exports = {
    Object3DModel: Object3DModel,
};
