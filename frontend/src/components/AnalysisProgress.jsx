import { Check, Circle, Loader2 } from 'lucide-react';

/**
 * AnalysisProgress - Professional progress interface shown during repository analysis.
 */
const AnalysisProgress = ({ url, progress = 0 }) => {
  // Progress steps
  const steps = [
    { id: 'connect', label: 'Connecting to GitHub', status: 'completed' },
    { id: 'download', label: 'Downloading repository', status: 'completed' },
    { id: 'scan', label: 'Scanning files', status: 'completed' },
    { id: 'understand', label: 'Understanding code structure', status: 'active' },
    { id: 'index', label: 'Creating knowledge index', status: 'pending' },
    { id: 'prepare', label: 'Preparing AI', status: 'pending' },
  ];

  // Determine which steps are completed based on progress
  const getStepStatus = (index) => {
    if (progress >= (index + 1) * (100 / steps.length)) {
      return 'completed';
    }
    if (progress >= index * (100 / steps.length)) {
      return 'active';
    }
    return 'pending';
  };

  const StepIcon = ({ status }) => {
    if (status === 'completed') {
      return <Check size={16} />;
    }
    if (status === 'active') {
      return <Loader2 size={16} className="animate-spin" />;
    }
    return <Circle size={16} />;
  };

  return (
    <div className="analysis-screen">
      <div className="analysis-container animate-fadeIn">
        <div className="surface-card shadow-soft-lg">
          <div className="analysis-body">
            {/* Header */}
            <div className="analysis-header">
              <div className="analysis-logo-wrap">
                <div className="analysis-logo-outer">
                  <div className="analysis-logo-inner">
                    <span>A</span>
                  </div>
                </div>
              </div>
              <h2 className="analysis-title">
                Analyzing Repository
              </h2>
              <p className="analysis-url">
                {url || 'Processing your repository...'}
              </p>
            </div>

            {/* Progress bar */}
            <div className="progress-section">
              <div className="progress-track">
                <div
                  className="progress-fill"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <div className="progress-info">
                <span className="progress-percent">{Math.round(progress)}% complete</span>
                <span>
                  Step {Math.min(Math.ceil((progress / 100) * steps.length), steps.length)} of{' '}
                  {steps.length}
                </span>
              </div>
            </div>

            {/* Steps */}
            <div className="progress-steps">
              {steps.map((step, index) => {
                const status = getStepStatus(index);
                return (
                  <div
                    key={step.id}
                    className={`progress-step ${status}`}
                  >
                    <div className={`step-icon ${status}`}>
                      <StepIcon status={status} />
                    </div>
                    <span className={`step-label ${status}`}>
                      {step.label}
                    </span>
                    {status === 'completed' && (
                      <span className="step-status done">Done</span>
                    )}
                    {status === 'active' && (
                      <span className="step-status processing">Processing...</span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisProgress;