import extractionMEDimlFeatures from "./possibleSettings/extractionMEDiml/extractionMEDimlFeatures.js"

// Node parameters for Extraction module of extraction tab
const nodesParams = {
  morph: {
    type: "featuresNode",
    classes: "object ntf morphological",
    nbInput: 0,
    nbOutput: 0,
    input: [],
    output: [],
    img: "features.svg",
    title: "MORPH",
    possibleSettings: { defaultSettings: extractionMEDimlFeatures.morph }
  },
  li: {
    type: "featuresNode",
    classes: "object ntf local_intensity",
    nbInput: 0,
    nbOutput: 0,
    input: [],
    output: [],
    img: "features.svg",
    title: "LI",
    possibleSettings: { defaultSettings: extractionMEDimlFeatures.li }
  },
  stats: {
    type: "featuresNode",
    classes: "object ntf statistical",
    nbInput: 0,
    nbOutput: 0,
    input: [],
    output: [],
    img: "features.svg",
    title: "STATS",
    possibleSettings: { defaultSettings: extractionMEDimlFeatures.stats }
  },
  ih: {
    type: "featuresNode",
    classes: "object ntf intensity_histogram",
    nbInput: 0,
    nbOutput: 0,
    input: [],
    output: [],
    img: "features.svg",
    title: "IH",
    possibleSettings: { defaultSettings: extractionMEDimlFeatures.ih }
  },
  ivh: {
    type: "featuresNode",
    classes: "object ntf ivh",
    nbInput: 0,
    nbOutput: 0,
    input: [],
    output: [],
    img: "features.svg",
    title: "IVH",
    possibleSettings: { defaultSettings: extractionMEDimlFeatures.ivh }
  },
  glcm: {
    type: "featuresNode",
    classes: "object tf glcm",
    nbInput: 0,
    nbOutput: 0,
    input: [],
    output: [],
    img: "features.svg",
    title: "GLCM",
    possibleSettings: { defaultSettings: extractionMEDimlFeatures.glcm }
  },
  gldzm: {
    type: "featuresNode",
    classes: "object tf gldzm",
    nbInput: 0,
    nbOutput: 0,
    input: [],
    output: [],
    img: "features.svg",
    title: "GLDZM",
    possibleSettings: { defaultSettings: extractionMEDimlFeatures.gldzm }
  },
  glrlm: {
    type: "featuresNode",
    classes: "object tf glrlm",
    nbInput: 0,
    nbOutput: 0,
    input: [],
    output: [],
    img: "features.svg",
    title: "GLRLM",
    possibleSettings: { defaultSettings: extractionMEDimlFeatures.glrlm }
  },
  glszm: {
    type: "featuresNode",
    classes: "object tf glszm",
    nbInput: 0,
    nbOutput: 0,
    input: [],
    output: [],
    img: "features.svg",
    title: "GLSZM",
    possibleSettings: { defaultSettings: extractionMEDimlFeatures.glszm }
  },
  ngldm: {
    type: "featuresNode",
    classes: "object tf ngldm",
    nbInput: 0,
    nbOutput: 0,
    input: [],
    output: [],
    img: "features.svg",
    title: "NGLDM",
    possibleSettings: { defaultSettings: extractionMEDimlFeatures.ngldm }
  },
  ngtdm: {
    type: "featuresNode",
    classes: "object tf ngtdm",
    nbInput: 0,
    nbOutput: 0,
    input: [],
    output: [],
    img: "features.svg",
    title: "NGTDM",
    possibleSettings: { defaultSettings: extractionMEDimlFeatures.ngtdm }
  }
}

export default nodesParams
