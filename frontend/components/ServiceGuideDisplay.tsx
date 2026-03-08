import { ServiceGuide } from '../types/chat'
import styles from '../styles/ServiceGuide.module.css'

interface ServiceGuideDisplayProps {
  guide: ServiceGuide
}

export default function ServiceGuideDisplay({ guide }: ServiceGuideDisplayProps) {
  return (
    <div className={styles.guideContainer} aria-label="Service Guide">
      <div className={styles.header}>
        <h3 className={styles.serviceName}>{guide.service_name}</h3>
        <p className={styles.description}>{guide.description}</p>
      </div>

      {guide.steps && guide.steps.length > 0 && (
        <div className={styles.stepsSection}>
          <h4>Steps to Follow</h4>
          <ol className={styles.stepsList}>
            {guide.steps.map((step) => (
              <li key={step.step_number} className={styles.step}>
                <div className={styles.stepHeader}>
                  <span className={styles.stepNumber}>Step {step.step_number}</span>
                  <span className={styles.duration}>{step.estimated_duration}</span>
                </div>
                <p className={styles.stepDescription}>{step.description}</p>
                <div className={styles.stepMeta}>
                  {step.online_available && (
                    <span className={styles.badge}>🌐 Available Online</span>
                  )}
                  {step.requires_in_person && (
                    <span className={styles.badge}>🏢 In-Person Required</span>
                  )}
                </div>
                {step.notes && (
                  <p className={styles.stepNotes}>📝 {step.notes}</p>
                )}
              </li>
            ))}
          </ol>
        </div>
      )}

      {guide.processing_time && (
        <div className={styles.processingSection}>
          <h4>Processing Time</h4>
          <p className={styles.typicalTime}>
            <strong>Typical:</strong> {guide.processing_time.typical}
          </p>
          <p className={styles.timeRange}>
            Range: {guide.processing_time.minimum} - {guide.processing_time.maximum}
          </p>
          {guide.processing_time.factors && guide.processing_time.factors.length > 0 && (
            <div className={styles.factors}>
              <strong>Factors affecting processing time:</strong>
              <ul>
                {guide.processing_time.factors.map((factor, idx) => (
                  <li key={idx}>{factor}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {guide.official_portal_url && (
        <div className={styles.portalSection}>
          <h4>Official Portal</h4>
          <a 
            href={guide.official_portal_url} 
            target="_blank" 
            rel="noopener noreferrer"
            className={styles.portalLink}
          >
            🔗 Visit Official Government Portal
          </a>
        </div>
      )}

      {guide.contact_info && (
        <div className={styles.contactSection}>
          <h4>Contact Information</h4>
          <dl className={styles.contactList}>
            {guide.contact_info.phone && (
              <>
                <dt>Phone:</dt>
                <dd>{guide.contact_info.phone}</dd>
              </>
            )}
            {guide.contact_info.email && (
              <>
                <dt>Email:</dt>
                <dd>{guide.contact_info.email}</dd>
              </>
            )}
            {guide.contact_info.helpline && (
              <>
                <dt>Helpline:</dt>
                <dd>{guide.contact_info.helpline}</dd>
              </>
            )}
            {guide.contact_info.address && (
              <>
                <dt>Address:</dt>
                <dd>{guide.contact_info.address}</dd>
              </>
            )}
          </dl>
        </div>
      )}
    </div>
  )
}
