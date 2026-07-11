# CVA monitoring and diagnosis guidance

## Model training

The paper trains CVA from normal data. For varying operating conditions, one normal data set is not enough to represent all normal dynamics. The paper constructs past and future Hankel matrices separately for normal data sets and then combines them.

The final selected configuration is:

- training data: T2 and T3 combined
- monitoring validation normal set: T1
- p = 15 past observations
- f = 15 future observations
- retained state dimension r = 25
- confidence level alpha = 0.99
- variables 1-23 for Fault Cases 1-5
- variables 1-24 for Fault Case 6

For r = 25, the T2/T3 training combination gives T2 threshold 1753.97, Q threshold 6940.73, T2 false alarm rate 0%, and Q false alarm rate about 0.2121% on T1.

## Indicators

T2 measures variation in the retained canonical variate space. Q, also called SPE, measures squared prediction error in the residual space. Some faults appear mainly in retained state variation; others appear as residual variation. A detection event is considered when either indicator exceeds its upper control limit.

## Thresholds

KDE thresholds are important because the facility is nonlinear. Gaussian threshold assumptions can produce unrealistically low thresholds and over-threshold behavior before fault introduction. KDE generally reduces false alarms and makes detection more reliable.

## Diagnosis from contribution plots

After detection, contribution plots rank variables responsible for the T2 or Q statistic. The paper finds T2 contribution plots more consistently related to the seeded physical fault, while Q contribution plots can be less clear because Q is oversensitive and spreads contribution across multiple variables.

## Practical diagnosis rules

- If x7/PT408-PT403 dominates, suspect top separator input blockage at VC404.
- If x13, x6 and x2 dominate with oscillatory behavior, suspect slugging.
- If x24/PT417 changes abruptly, suspect pressurization of the isolated 2 inch line.
- If water-side variables x9/x22/x23 dominate gradually, suspect water line blockage, but expect this case to be difficult.
- If air-side variables x1/x8/x21 dominate gradually, suspect air line blockage.
- If riser/top separator flow is reduced while separator bypass symptoms appear, suspect open direct bypass.

## Known interpretation cautions

- Q often detects earlier but can raise more false alarms.
- T2 contribution plots are usually better for fault identification in this benchmark.
- Fault Case 2 remains difficult; a weak or missing Q response does not rule it out.
- A new normal operating regime outside the training data requires updating the model and thresholds.
