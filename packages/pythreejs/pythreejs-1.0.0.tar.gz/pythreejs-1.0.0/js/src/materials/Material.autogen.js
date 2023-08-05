//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;

var PlaneModel = require('../math/Plane.autogen.js').PlaneModel;

var MaterialModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            alphaTest: 0,
            blendDst: "OneMinusSrcAlphaFactor",
            blendDstAlpha: 0,
            blending: "NormalBlending",
            blendSrc: "SrcAlphaFactor",
            blendSrcAlpha: 0,
            blendEquation: "AddEquation",
            blendEquationAlpha: 0,
            clipIntersection: false,
            clippingPlanes: [],
            clipShadows: false,
            colorWrite: true,
            defines: null,
            depthFunc: "LessEqualDepth",
            depthTest: true,
            depthWrite: true,
            dithering: false,
            flatShading: false,
            fog: true,
            lights: true,
            name: "",
            opacity: 1,
            overdraw: 0,
            polygonOffset: false,
            polygonOffsetFactor: 0,
            polygonOffsetUnits: 0,
            precision: null,
            premultipliedAlpha: false,
            shadowSide: null,
            side: "FrontSide",
            transparent: false,
            type: "Material",
            vertexColors: "NoColors",
            visible: true,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Material();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);
        this.three_nested_properties.push('clippingPlanes');

        this.props_created_by_three['type'] = true;
        this.enum_property_types['blendDst'] = 'BlendFactors';
        this.enum_property_types['blending'] = 'BlendingMode';
        this.enum_property_types['blendSrc'] = 'BlendFactors';
        this.enum_property_types['blendEquation'] = 'Equations';
        this.enum_property_types['depthFunc'] = 'DepthMode';
        this.enum_property_types['shadowSide'] = 'Side';
        this.enum_property_types['side'] = 'Side';
        this.enum_property_types['vertexColors'] = 'Colors';

        this.property_converters['alphaTest'] = 'convertFloat';
        this.property_converters['blendDst'] = 'convertEnum';
        this.property_converters['blendDstAlpha'] = 'convertFloat';
        this.property_converters['blending'] = 'convertEnum';
        this.property_converters['blendSrc'] = 'convertEnum';
        this.property_converters['blendSrcAlpha'] = 'convertFloat';
        this.property_converters['blendEquation'] = 'convertEnum';
        this.property_converters['blendEquationAlpha'] = 'convertFloat';
        this.property_converters['clipIntersection'] = 'convertBool';
        this.property_converters['clippingPlanes'] = 'convertThreeTypeArray';
        this.property_converters['clipShadows'] = 'convertBool';
        this.property_converters['colorWrite'] = 'convertBool';
        this.property_converters['defines'] = null;
        this.property_converters['depthFunc'] = 'convertEnum';
        this.property_converters['depthTest'] = 'convertBool';
        this.property_converters['depthWrite'] = 'convertBool';
        this.property_converters['dithering'] = 'convertBool';
        this.property_converters['flatShading'] = 'convertBool';
        this.property_converters['fog'] = 'convertBool';
        this.property_converters['lights'] = 'convertBool';
        this.property_converters['name'] = null;
        this.property_converters['opacity'] = 'convertFloat';
        this.property_converters['overdraw'] = 'convertFloat';
        this.property_converters['polygonOffset'] = 'convertBool';
        this.property_converters['polygonOffsetFactor'] = 'convertFloat';
        this.property_converters['polygonOffsetUnits'] = 'convertFloat';
        this.property_converters['precision'] = null;
        this.property_converters['premultipliedAlpha'] = 'convertBool';
        this.property_converters['shadowSide'] = 'convertEnum';
        this.property_converters['side'] = 'convertEnum';
        this.property_converters['transparent'] = 'convertBool';
        this.property_converters['type'] = null;
        this.property_converters['vertexColors'] = 'convertEnum';
        this.property_converters['visible'] = 'convertBool';

        this.property_assigners['defines'] = 'assignDict';

    },

}, {

    model_name: 'MaterialModel',

    serializers: _.extend({
        clippingPlanes: { deserialize: widgets.unpack_models },
    },  ThreeModel.serializers),
});

module.exports = {
    MaterialModel: MaterialModel,
};
