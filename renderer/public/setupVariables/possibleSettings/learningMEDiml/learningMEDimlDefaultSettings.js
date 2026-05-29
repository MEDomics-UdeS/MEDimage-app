const learningMEDimlDefaultSettings = {
  // split
  design : {
    path_outcome_file: "",
    path_ws_experiments: "",
    outcome_name: "",
    path_save_experiments: "",
    method: "all_learn",
  },

  // design
  split : {
    expName: "",
    active_method: ["cv"],
    Random: {
      method: "SubSampling",
      nSplits: 10,
      stratifyInstitutions: true,
      testProportion: 0.33,
      seed: 54288
    },
    cv: {
      nFolds: 10,
      seed: 54288
    }
  },

  // data
  data : {
      nameType: "Radiomics",
      featuresFiles: []
  },

  // variables 
  radiomics_learner : {
    model: "XGBoost",
    XGBoost: {
      varImportanceThreshold: 0.3,
      optimizeThreshold: true,
      finalizeModel: true,
      nameSave: "xgboost_5perc",
      optimizationMetric: "MCC",
      seed: 54288
    }
  },
  //settings
  settings: {
    normalization: "combat",
    fSetReduction: "FDA",
    algorithm: "XGBoost"
  },

  // normalize
  normalization : {
    method: "combat",
  },

  //fsr
  feature_reduction : {
    method: "FDA",
    FDA: {
        nSplits: 100,
        corrType: "Spearman",
        threshStableStart: 0.5,
        threshInterCorr: 0.7,
        minNfeatStable: 100,
        minNfeatInterCorr: 60,
        minNfeat: 10,
        seed: 54288
    }
  },
  
  //cleaning
  cleaning : {
    default: {
      feature: {
        continuous: {
          missingCutoffps: 0.25,
          covCutoff: 0.1,
          missingCutoffpf: 0.1,
          imputation: "mean"
        }
      }
    }
  },
  analyze : {
    histogram: true,
    tree: true,
    heatmap: true,
    optimalLevel: true,
    histParams: {
      sortOption: "importance"
    },
    heatmapParams: {
      metric: "AUC_mean",
      extraMetrics: "Sensitivity_mean,Specificity_mean",
      pValues: true,
      pValuesMethod: "delong",
      title: ""
    }
  }
}

export default learningMEDimlDefaultSettings
