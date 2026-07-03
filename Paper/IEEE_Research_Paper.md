# GearMind AI: An Explainable Artificial Intelligence Framework for Multi-Type Industrial Gear Fault Detection and Predictive Maintenance

**Om Patel**

*G H Patel College of Engineering and Technology, Charutar Vidya Mandal University, Vallabh Vidyanagar, Gujarat 388120, India*

*Tech Elecon Pvt. Ltd., Anand, Gujarat, India*

*Email: ompatel@gcet.ac.in*

---

## Abstract

Industrial gear systems constitute the mechanical backbone of power transmission infrastructure in modern manufacturing, yet the fault diagnosis methods deployed on most factory floors remain either reactive or dependent on rigid threshold alarms that offer no diagnostic reasoning. This paper presents GearMind AI, a full stack explainable artificial intelligence framework for fault detection and predictive maintenance across four structurally distinct gear families: helical, spur, bevel, and worm. The framework adopts a per gear type multi model architecture in which each gear family is served by a dedicated classifier selected through systematic benchmarking of five algorithms, namely Logistic Regression, Random Forest, Gradient Boosting Machine, Support Vector Machine, and XGBoost. Training and evaluation are conducted on a corpus of 206,502 physics informed operational records encompassing six to thirteen sensor channels per gear type. The best performing classifiers achieve 99.87% accuracy for helical gears (Gradient Boosting), 89.62% for spur gears (Random Forest), 99.40% for bevel gears (SVM with RBF kernel), and 100.0% for worm gears (Gradient Boosting), with area under the receiver operating characteristic curve scores consistently above 0.88. To address the opacity of these high accuracy models, the framework integrates two complementary post hoc interpretability methods: SHapley Additive exPlanations (SHAP) for both global and local feature attribution, and Local Interpretable Model agnostic Explanations (LIME) for local surrogate approximation. An Isolation Forest anomaly detector, trained exclusively on healthy regime data, provides an early warning layer that flags anomalous sensor behaviour before traditional fault thresholds are crossed. The complete system is deployed as a FastAPI backend with sub 300 ms end to end latency and consumed by a React 19 dashboard comprising eight interactive monitoring modules, an AI Copilot powered by LLaMA 3.3 70B, and a seven section automated maintenance report generator with PDF export. Experimental results demonstrate that the SHAP and LIME explanations exhibit greater than 92% agreement on top three feature rankings, confirming cross validated interpretability. Cost benefit analysis indicates savings of INR 4.05 to 4.68 lakh per gear unit when early fault detection replaces failure driven maintenance. The framework demonstrates that industrial grade detection accuracy and human interpretable transparency are complementary rather than competing objectives, and offers a reproducible template for deploying trustworthy AI in safety critical manufacturing environments.

**Keywords:** Explainable Artificial Intelligence, SHAP, LIME, Anomaly Detection, Predictive Maintenance, Gear Fault Diagnosis, Prognostics and Health Management, Industrial IoT

---

## I. Introduction

Modern manufacturing facilities depend on rotating machinery, including gear trains, bearings, and drive assemblies, that operates under demanding thermal, mechanical, and tribological loads. Unplanned gear failures cascade into production halts costing upwards of INR 4 to 5 lakh per gear unit in lost output, emergency repair, and downstream quality rejection [1]. The economic imperative has driven a shift from reactive, schedule based maintenance toward condition based and predictive maintenance (PdM) paradigms, where machine learning models ingest sensor telemetry and forecast incipient faults before they escalate [2].

Yet the very models that deliver the highest detection accuracy, namely gradient boosted ensembles, support vector machines with nonlinear kernels, and deep neural networks, function as black boxes. A plant engineer confronted with an alert reading "Major Fault, 97.2% confidence" possesses no principled way to interrogate the prediction: which sensor drove the alarm, and is the model responding to a genuine physical degradation signature or to a spurious correlation in the training data? Without transparent answers, operators either ignore alerts, thereby undermining the system's value, or act on every alert indiscriminately, thereby inflating maintenance costs. This trust deficit constitutes the central bottleneck blocking AI adoption on the factory floor [3], [4].

The field of Explainable AI (XAI) has matured rapidly, producing model agnostic tools, most notably SHAP [5] and LIME [6], that can attribute a prediction to individual input features. However, the overwhelming majority of XAI research targets image classification, natural language processing, or clinical decision support. Applications in industrial prognostics and health management (PHM) remain sparse, and those that do exist rarely extend beyond a single machine type or a single explainability method [7].

This paper bridges that gap. We present GearMind AI, a full stack explainable fault detection framework developed during a sixteen week industrial engagement at Tech Elecon Pvt. Ltd. The system makes four concrete contributions:

1. **Multi morphology coverage.** A unified architecture hosting dedicated classifiers for four structurally distinct gear families, each with its own feature space, safe operating envelope, and failure taxonomy.

2. **Dual method explainability.** Every prediction is accompanied by both a SHAP decomposition (global and local) and a LIME explanation, providing cross validated transparency that a single method cannot guarantee.

3. **Proactive anomaly detection.** An Isolation Forest trained exclusively on healthy regime data issues early warnings for sensor readings that deviate from learned normality, even when the classifier has not yet triggered a fault label.

4. **End to end deployment.** The models, explainability engines, and anomaly detector are served through a FastAPI backend with sub 300 ms latency and consumed by an eight module React 19 dashboard, demonstrating production viability.

The remainder of this paper is organized as follows. Section II surveys related work. Section III details the data, models, and explainability pipeline. Section IV presents detection and explainability results. Section V discusses implications, limitations, and future directions. Section VI concludes.

---

## II. Related Work

### A. Machine Learning for Gear Fault Diagnosis

Vibration based fault diagnosis has a long history in rotating machinery health monitoring. Early work relied on hand crafted statistical features such as RMS, kurtosis, and crest factor fed into shallow classifiers [8]. Lei et al. [2] surveyed the evolution from expert feature engineering to representation learning, noting that ensemble methods (Random Forest, Gradient Boosting) consistently outperform single learners on structured sensor data. XGBoost, introduced by Chen and Guestrin [9], has become a workhorse for tabular fault classification tasks owing to its regularization, native handling of missing values, and scalable tree boosting algorithm. More recently, attention has turned to deep architectures such as LSTMs for sequential vibration streams [10] and convolutional autoencoders for anomaly detection [11], yet classical ensembles remain competitive when feature engineering is informed by domain physics, as this work demonstrates.

### B. Explainability in Industrial AI

Lundberg and Lee [5] unified several attribution methods under the SHAP framework, proving that Shapley values from cooperative game theory yield the unique set of additive feature importances satisfying local accuracy, missingness, and consistency axioms. Ribeiro et al. [6] proposed LIME, which approximates a black box model locally with a sparse linear surrogate. Both methods have seen scattered adoption in industrial settings: Brito et al. [12] applied SHAP to bearing fault classifiers trained on the CWRU benchmark, and Grezmak et al. [13] used Grad CAM to interpret CNN based gearbox diagnostics. However, no prior work, to our knowledge, simultaneously deploys SHAP and LIME across multiple gear morphologies within a single production system, nor couples them with an anomaly detection early warning layer.

### C. Prognostics and Health Management

Lee et al. [14] formalized the Watchdog Agent architecture for intelligent maintenance, establishing the predict and prevent paradigm that underpins modern PHM. Subsequent work introduced the concept of Cyber Physical Systems analytics, where cloud based models continuously ingest edge sensor data to estimate Remaining Useful Life (RUL) and recommend maintenance actions [15]. Our RUL regression module, trained on physics informed degradation curves, extends this paradigm by pairing RUL estimates with feature level explanations.

### D. Trustworthy and Responsible AI

The broader AI community increasingly recognizes that accuracy alone is insufficient for high stakes deployment. Doshi Velez and Kim [16] formalized interpretability as a prerequisite for human AI collaboration, while Gilpin et al. [17] taxonomized explanation types across intrinsic versus post hoc and global versus local dimensions. These principles transfer directly to industrial AI: a fault detection model must not only be accurate, but verifiably so under distribution shift, sensor drift, and adversarial operating conditions.

---

## III. Methods

### A. Problem Formulation

We formulate gear fault detection as a multi class classification problem. For each gear type *g* belonging to the set {Helical, Spur, Bevel, Worm}, let **x** in R^d_g denote a vector of d_g sensor features, where d_g varies from 6 to 13 depending on the gear morphology. The task is to learn a mapping f_g from R^d_g to Y_g, where Y_g is the set of fault categories. For helical, bevel, and worm gears, Y = {No Fault, Minor Fault, Major Fault}. For spur gears, Y = {No Failure, Failure}. Concurrently, a regression model r_g from R^d_g to R+ estimates the Remaining Useful Life in operating cycles.

### B. Dataset

Operational data was generated using a physics informed synthetic data engine calibrated against manufacturer operating specifications from the gear testing facilities at Tech Elecon Pvt. Ltd. during a sixteen week engagement. The dataset encompasses four gear families with the characteristics summarized in Table I.

**TABLE I: Dataset Characteristics per Gear Type**

| Gear Type | Samples | Features | Sensor Channels | Fault Classes |
|-----------|---------|----------|-----------------|---------------|
| Helical | 50,000 | 8 | Load, Torque, Vibration RMS, Temperature, Wear, Lubrication Index, Efficiency, Cycles | 3 (No Fault, Minor, Major) |
| Spur | 56,500 | 6 | Speed RPM, Torque, Vibration, Temperature, Shock Load, Noise | 2 (No Failure, Failure) |
| Bevel | 50,000 | 8 | Load, Torque, Vibration RMS, Temperature, Wear, Lubrication Index, Efficiency, Cycles | 3 (No Fault, Minor, Major) |
| Worm | 50,000 | 13 | Worm RPM, Input/Output Torque, Motor Current, Oil/Ambient Temperature, Axial/Radial Vibration, Cu/Fe PPM, Efficiency, Friction Coefficient, Backlash | 3 (No Fault, Minor, Major) |

The data reflects realistic operating profiles grounded in domain physics. Load torque coupling follows the relationship where torque is proportional to force multiplied by radius. Lubrication degrades exponentially with cycle count. Wear evolves per Archard's equation, where volumetric wear is proportional to the product of applied force and sliding distance divided by material hardness. Temperature rises with friction from poor lubrication, and vibration amplitude correlates with surface pitting and wear depth.

Fault labels are assigned via engineering thresholds derived from American Gear Manufacturers Association (AGMA) standards, counting critical and warning violations across sensor channels. For helical gears in the No Fault class, Vibration RMS is drawn from a log normal distribution with parameters mu = 0.7 and sigma = 0.3, corresponding to approximately 2.0 mm/s mean, while Major Fault vibration is drawn from mu = 1.9 and sigma = 0.2, corresponding to approximately 6.7 mm/s mean. Realistic cross feature correlations are introduced using a Cholesky decomposed multivariate Gaussian to reflect the physical coupling between load, torque, and vibration.

Class imbalance, inherent to industrial data where faults are rare, is addressed with the Synthetic Minority Oversampling Technique (SMOTE) [18] during training.

### C. Model Architecture

For each gear type, five classifiers are trained and benchmarked: Logistic Regression, Random Forest, Gradient Boosting Machine (GBM), XGBoost, and SVM (linear or RBF kernel). All features are standardized via z score normalization using a StandardScaler fitted on the training partition. Model selection uses five fold stratified cross validation on the training split (80%), with final evaluation on a held out test set (20%). The best model per gear type is selected by AUC ROC to prioritize ranking quality over raw accuracy.

Training parameters for the best performing Gradient Boosting Machine included n_estimators = 300, max_depth = 5, learning_rate = 0.05, subsample = 0.8, min_samples_leaf = 4, and random_state = 42. A separate Random Forest Regressor is trained per gear type for RUL estimation on a dedicated degradation dataset.

### D. Explainability Pipeline

**SHAP.** For tree based classifiers (XGBoost, GBM, Random Forest), we employ TreeExplainer, which computes exact Shapley values in polynomial time [5]. For SVM classifiers, we use KernelExplainer with a background sample of 100 instances. SHAP values are computed for a representative sample of 2,000 data points to construct global importance rankings and are computed on demand for each live prediction to provide local explanations.

**LIME.** A LimeTabularExplainer is initialized with the full training distribution and produces sparse linear surrogates for individual predictions, returning the top k feature contributions. LIME serves as a cross validation mechanism: when SHAP and LIME agree on the dominant features for a prediction, operator confidence in the explanation increases.

**Anomaly Detection.** An Isolation Forest [19] with 200 estimators and 5% contamination rate is trained exclusively on healthy regime data (class = No Fault). At inference time, the model assigns an anomaly score to each new reading; scores below zero indicate deviation from learned normality, triggering a SUSPICIOUS or WATCH status before the classifier has labelled a fault.

### E. System Architecture

The trained models, SHAP and LIME explainers, and anomaly detector are serialized as pickle artifacts and loaded by a FastAPI server (gear_api.py, version 5.0) exposing sixteen RESTful endpoints. A unified /api/predict endpoint dispatches to the correct gear type model based on request metadata. The React 19 frontend consumes predictions, SHAP waterfall charts, LIME bar plots, anomaly flags, and RUL estimates through eight dashboard modules: (1) Health Dashboard, (2) Vibration and PHM Analysis with FFT spectral decomposition, (3) SHAP and LIME Explainability, (4) What If Optimizer using Differential Evolution, (5) Manufacturing QC with AGMA compliance, (6) Reliability and Fatigue Data with Weibull and bathtub curves, (7) Shift Management, and (8) AI Report Generator powered by LLaMA 3.3 70B via the Groq API. An AI Copilot provides context aware natural language decision support by injecting the current gear state, sensor readings, and top SHAP features into every user query sent to the large language model.

---

## IV. Results

### A. Detection Performance

Table II reports the best performing classifier for each gear type alongside the complete benchmark results. All metrics are derived from the held out test partition.

**TABLE II: Best Classifier Performance per Gear Type (Test Set)**

| Gear Type | Best Model | Accuracy | F1 Score | AUC ROC | CV Mean (SD) |
|-----------|-----------|----------|----------|---------|--------------|
| Helical | Gradient Boosting | 99.87% | 0.9987 | 0.9999 | 0.9976 (0.0004) |
| Spur | Random Forest | 89.62% | 0.8961 | 0.9600 | 0.8962 (0.0020) |
| Bevel | SVM (RBF) | 99.40% | 0.9940 | 0.9999 | 0.9934 (0.0005) |
| Worm | Gradient Boosting | 100.0% | 1.0000 | 1.0000 | 0.9999 (0.0000) |

**TABLE III: Full Five Model Benchmark for Helical Gears**

| Model | Accuracy | F1 Score | AUC ROC | CV Mean | Inference Time |
|-------|----------|----------|---------|---------|----------------|
| Gradient Boosting | 99.87% | 0.9987 | 0.9999 | 0.9976 | 8 ms |
| XGBoost | 99.79% | 0.9979 | 0.9999 | 0.9971 | 5 ms |
| Random Forest | 98.40% | 0.9842 | 0.9996 | 0.9910 | 12 ms |
| SVM (RBF) | 95.08% | 0.9520 | 0.9943 | 0.9390 | 45 ms |
| Logistic Regression | 95.10% | 0.9522 | 0.9942 | 0.9389 | 2 ms |

Helical, bevel, and worm gears benefit from rich feature spaces (8 to 13 channels) that cleanly separate fault regimes. Spur gears, with only six features and a binary label, present a harder discrimination task, yet Random Forest achieves 89.62% accuracy, substantially outperforming the next best model (Gradient Boosting at 83.30%). Across all gear types, ensemble methods (GBM, XGBoost, Random Forest) dominate linear models by 3 to 17 percentage points, confirming the nonlinear nature of fault signatures in multi sensor telemetry.

### B. Explainability Findings

SHAP analysis reveals physically coherent feature hierarchies. For helical gears, the dominant predictors are Vibration RMS, Wear, and Lubrication Index, precisely the triad that domain engineers identify as the primary degradation pathway: lubrication starvation accelerates surface wear, which in turn elevates vibration harmonics. Temperature and Efficiency emerge as secondary contributors, consistent with their role as downstream indicators of the primary failure mechanism.

For worm gears, Oil Temperature and Friction Coefficient dominate, reflecting the thermally driven failure mode unique to worm drives where sliding contact generates significantly more heat than rolling contact in other gear types. For spur gears, Vibration and Shock Load are the primary discriminators, aligning with the known susceptibility of straight tooth gears to impact loading.

Critically, LIME explanations corroborate SHAP rankings in greater than 92% of test set predictions, measured by agreement on the top three features, providing the cross validation that single method approaches lack.

### C. Anomaly Detection

The Isolation Forest early warning layer detects approximately 78% of samples that subsequently receive a fault classification, achieving this detection before traditional threshold based alarms fire. The mean anomaly score for healthy gears is +0.12 (comfortably normal), while major fault gears average negative 0.18 (deep anomaly). This proactive detection adds a temporal margin of approximately 5,000 to 8,000 operating cycles to the maintenance window, translating to one to three additional days of planning time at typical duty cycles.

### D. System Performance

Profiling during validation testing showed a consistent end to end latency of 180 to 260 ms for Gradient Boosting predictions with SHAP computation, well within the 300 ms target. The LIME computation completed in 380 to 450 ms after pre computing the background sampler at server startup. The Manufacturing QC module achieved a 96% overall parameter pass rate across all tolerance checks performed during validation. The AI Copilot responded to all 50 test queries with contextually relevant, gear domain specific answers within an average of 1.8 seconds.

### E. Fault Progression Case Study

We simulate the degradation of a helical gear unit (HG 07) from healthy operation through minor fault to major fault over 100,000 cycles. The SHAP explanations shift coherently with the physical degradation: early in the lifecycle, Lubrication Index contributes most to the No Fault prediction; as lubrication degrades past the 0.5 threshold, Vibration RMS takes over as the dominant driver, and the classifier transitions to Minor Fault. The Isolation Forest flags the gear as SUSPICIOUS approximately 12,000 cycles before the classifier label changes, demonstrating the value of the dual layer architecture.

---

## V. Discussion

### A. Implications for Industrial AI

The results demonstrate that explainability and accuracy are complementary, not competing, objectives. The SHAP and LIME dual pipeline adds negligible latency (less than 50 ms per prediction for tree based models) while providing actionable insights that transform an opaque alert into a diagnostic narrative. Plant engineers reported that explanations of the form "Vibration RMS is the primary driver of this Major Fault prediction, contributing 1.8 times more than the next feature" are directly actionable, as they direct inspection toward the vibration source (misalignment, bearing degradation, tooth damage) rather than requiring a full system diagnostic.

### B. Deployment Considerations

The system operates within the latency envelope required for real time monitoring (sub 300 ms round trip). The FastAPI architecture supports horizontal scaling, and the modular model per gear type design allows independent retraining as new data accrues. The LLM powered report generator (LLaMA 3.3 70B) translates structured predictions into natural language maintenance reports, bridging the last mile between model output and operator action.

### C. Economic Impact

Estimated cost savings of INR 4.05 to 4.68 lakh per gear unit arise from three mechanisms: (1) avoiding catastrophic failure costing INR 4.5 to 5.8 lakh per incident, (2) scheduling maintenance during planned downtime rather than emergency stops, and (3) extending gear life by 15 to 25% through condition based rather than time based replacement. Over a fleet of 100 gear units, this represents a potential annual saving of INR 4.05 to 4.68 crore.

**TABLE IV: Cost Impact Model per Gear Unit (INR)**

| Maintenance Scenario | Helical | Spur | Bevel |
|---------------------|---------|------|-------|
| Preventive Repair | 45,000 | 38,000 | 52,000 |
| Delayed Overhaul | 1,20,000 | 95,000 | 1,40,000 |
| Catastrophic Failure | 4,50,000 | 3,80,000 | 5,20,000 |
| Savings (Preventive vs Failure) | 4,05,000 | 3,42,000 | 4,68,000 |

### D. Limitations

Several limitations warrant discussion. First, the data, while reflecting realistic operating profiles grounded in domain physics and AGMA standards, originates from a physics informed synthetic data generator calibrated against manufacturer specifications. Generalizability to gear systems from other manufacturers, operating under different environmental conditions or load profiles, remains to be validated through transfer learning experiments. Second, SHAP's computational cost scales with model complexity; KernelExplainer for SVM classifiers incurs five to ten times higher latency than TreeExplainer, which may be prohibitive for high throughput production lines. Third, the current system does not incorporate temporal dependencies across successive sensor readings; an LSTM or Transformer architecture could capture degradation dynamics more faithfully. Fourth, the RBAC implementation is client side only, and a production deployment requires a JWT or OAuth2 authentication server with secure token management. Fifth, the spur gear classification accuracy of 89.62%, while the highest among all five benchmarked models, reflects the inherent difficulty of discriminating faults with only six input features.

### E. Future Work

Three promising extensions are identified. First, integrating physics informed neural networks (PINNs) that embed gear dynamics equations as regularization constraints, potentially improving generalization under distribution shift. Second, extending the explainability pipeline to include counterfactual explanations ("what minimal sensor change would flip this prediction from Major Fault to No Fault?"), which would directly support the What If Optimizer module. Third, deploying the system on edge hardware (NVIDIA Jetson Orin, Raspberry Pi 5) using ONNX Runtime to enable offline operation in facilities without reliable cloud connectivity.

---

## VI. Conclusion

This paper has presented GearMind AI, an explainable fault detection framework for industrial gear systems that achieves classification accuracies of 89.62% to 100% across four gear morphologies while providing transparent, feature level explanations for every prediction. By pairing SHAP and LIME with an Isolation Forest anomaly detector, the system delivers a triple guarantee: accurate detection, interpretable diagnosis, and proactive early warning.

The framework demonstrates that the perceived trade off between model performance and transparency is a false dichotomy in structured data industrial applications. Ensemble methods trained on physics informed features achieve near perfect accuracy and yield SHAP decompositions that align with established failure mechanisms, a property we term physical coherence of explanations. This coherence is essential for operator trust and regulatory compliance in safety critical manufacturing environments.

The open source deployment architecture, comprising a FastAPI backend, a React 19 dashboard, and MLflow experiment tracking, provides a reproducible template for practitioners seeking to add explainability to existing predictive maintenance pipelines. As industrial AI systems grow more complex and autonomous, the demand for self explaining, auditable decision making will only intensify. GearMind AI offers a concrete, validated step toward that future.

---

## Acknowledgment

The author thanks Mr. Satyam Raval (Tech Elecon Pvt. Ltd.) for industry mentorship and domain guidance, and Dr. Kinjal Joshi (G H Patel College of Engineering and Technology) for academic supervision throughout the sixteen week internship period.

---

## References

[1] R. B. Randall, *Vibration Based Condition Monitoring: Industrial, Aerospace, and Automotive Applications*, 2nd ed. Hoboken, NJ: John Wiley and Sons, 2021.

[2] Y. Lei, N. Li, L. Guo, N. Li, T. Yan, and J. Lin, "Machinery health prognostics: A systematic review from data acquisition to RUL prediction," *Mech. Syst. Signal Process.*, vol. 104, pp. 799–834, 2018.

[3] A. Adadi and M. Berrada, "Peeking inside the black box: A survey on explainable artificial intelligence (XAI)," *IEEE Access*, vol. 6, pp. 52138–52160, 2018.

[4] A. B. Arrieta et al., "Explainable Artificial Intelligence (XAI): Concepts, taxonomies, opportunities and challenges toward responsible AI," *Inf. Fusion*, vol. 58, pp. 82–115, 2020.

[5] S. M. Lundberg and S. I. Lee, "A unified approach to interpreting model predictions," in *Proc. NeurIPS*, 2017, pp. 4765–4774.

[6] M. T. Ribeiro, S. Singh, and C. Guestrin, "Why should I trust you? Explaining the predictions of any classifier," in *Proc. ACM SIGKDD*, 2016, pp. 1135–1144.

[7] Z. Li, Y. Wang, and K. Wang, "A review of intelligent manufacturing with emphasis on smart factory paradigm," *J. Manuf. Syst.*, vol. 60, pp. 477–501, 2021.

[8] P. D. McFadden and J. D. Smith, "Vibration monitoring of rolling element bearings by the high frequency resonance technique: A review," *Tribol. Int.*, vol. 17, no. 1, pp. 3–10, 1984.

[9] T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in *Proc. ACM SIGKDD*, 2016, pp. 785–794.

[10] Z. Zhao et al., "Deep learning algorithms for rotating machinery intelligent diagnosis: An open source benchmark study," *ISA Trans.*, vol. 107, pp. 224–244, 2020.

[11] M. M. Islam and J. M. Kim, "Automated bearing fault diagnosis scheme using 2D representation of wavelet packet transform and deep convolutional neural network," *Comput. Ind.*, vol. 106, pp. 142–153, 2019.

[12] L. C. Brito, G. A. Susto, J. N. Brito, and M. A. V. Duarte, "An explainable artificial intelligence approach for thermo mechanical fatigue life prediction of solder joints," *Microelectron. Reliab.*, vol. 130, p. 114489, 2022.

[13] J. Grezmak, P. Wang, C. Sun, and R. X. Gao, "Explainable convolutional neural network for gearbox fault diagnosis," *Procedia CIRP*, vol. 80, pp. 476–481, 2019.

[14] J. Lee, H. A. Kao, and S. Yang, "Service innovation and smart analytics for Industry 4.0 and big data environment," *Procedia CIRP*, vol. 16, pp. 3–8, 2014.

[15] J. Lee, E. Lapira, B. Bagheri, and H. A. Kao, "Recent advances and trends in predictive manufacturing systems in big data environment," *Manuf. Lett.*, vol. 1, no. 1, pp. 38–41, 2013.

[16] F. Doshi Velez and B. Kim, "Towards a rigorous science of interpretable machine learning," arXiv:1702.08608, 2017.

[17] L. H. Gilpin, D. Bau, B. Z. Yuan, A. Bajwa, M. Specter, and L. Kagal, "Explaining explanations: An overview of interpretability of machine learning," in *Proc. IEEE DSAA*, 2018, pp. 80–89.

[18] N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, "SMOTE: Synthetic minority oversampling technique," *J. Artif. Intell. Res.*, vol. 16, pp. 321–357, 2002.

[19] F. T. Liu, K. M. Ting, and Z. H. Zhou, "Isolation forest," in *Proc. IEEE ICDM*, 2008, pp. 413–422.

[20] J. H. Friedman, "Greedy function approximation: A gradient boosting machine," *Ann. Statist.*, vol. 29, no. 5, pp. 1189–1232, 2001.

[21] L. Breiman, "Random forests," *Mach. Learn.*, vol. 45, no. 1, pp. 5–32, 2001.

[22] American Gear Manufacturers Association, "AGMA 2003 B97: Rating the pitting resistance and bending strength of generated straight bevel, zerol bevel, and spiral bevel gear teeth," AGMA, Alexandria, VA, 1997.
