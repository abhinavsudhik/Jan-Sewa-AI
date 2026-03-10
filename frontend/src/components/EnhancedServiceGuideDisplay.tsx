import React from 'react';
import { EnhancedServiceGuide, OfficeLocation, RequiredDocument, OfficeVisitStep, OfficialWebsiteLink, ProcessingTimeline } from '../types/service';
import styles from './EnhancedServiceGuideDisplay.module.css';

interface EnhancedServiceGuideDisplayProps {
  guide: EnhancedServiceGuide;
}

/**
 * Enhanced Service Guide Display Component
 * 
 * Displays government service information in a structured format with all five
 * required categories: office locations, required documents, office visit sequence,
 * official websites, and processing timelines.
 * 
 * Validates: Requirements 1.1, 1.2, 1.3, 1.4, 9.2, 10.1, 10.3
 */
export function EnhancedServiceGuideDisplay({ guide }: EnhancedServiceGuideDisplayProps) {
  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  const renderOfficeLocations = (locations: OfficeLocation[]) => {
    if (!locations || locations.length === 0) {
      return <p className={styles.notAvailable}>Information not available</p>;
    }

    return (
      <div className={styles.locationsList}>
        {locations.map((location, index) => (
          <div key={index} className={styles.locationItem}>
            <h5 className={styles.locationName}>{location.name}</h5>
            <p className={styles.locationAddress}>
              {location.address}, {location.city}, {location.state} {location.postal_code}
            </p>
            {location.coordinates && (
              <p className={styles.coordinates}>
                Coordinates: {location.coordinates.latitude}, {location.coordinates.longitude}
              </p>
            )}
            {location.operating_hours && (
              <p className={styles.operatingHours}>
                Hours: {location.operating_hours}
              </p>
            )}
            {location.contact_phone && (
              <p className={styles.contactPhone}>
                Phone: {location.contact_phone}
              </p>
            )}
          </div>
        ))}
      </div>
    );
  };

  const renderRequiredDocuments = (documents: RequiredDocument[]) => {
    if (!documents || documents.length === 0) {
      return <p className={styles.notAvailable}>Information not available</p>;
    }

    return (
      <ul className={styles.documentsList}>
        {documents.map((doc, index) => (
          <li key={index} className={styles.documentItem}>
            <div className={styles.documentHeader}>
              <span className={styles.documentName}>{doc.document_name}</span>
              {!doc.is_mandatory && (
                <span className={styles.optionalBadge}>Optional</span>
              )}
            </div>
            {doc.description && (
              <p className={styles.documentDescription}>{doc.description}</p>
            )}
            {doc.copies_required > 1 && (
              <p className={styles.copiesRequired}>
                Copies required: {doc.copies_required}
              </p>
            )}
            {doc.format_requirements && (
              <p className={styles.formatRequirements}>
                Format: {doc.format_requirements}
              </p>
            )}
            {doc.alternatives && doc.alternatives.length > 0 && (
              <p className={styles.alternatives}>
                Alternatives: {doc.alternatives.join(', ')}
              </p>
            )}
          </li>
        ))}
      </ul>
    );
  };

  const renderOfficeVisitSequence = (sequence: OfficeVisitStep[]) => {
    if (!sequence || sequence.length === 0) {
      return <p className={styles.notAvailable}>Information not available</p>;
    }

    // Sort by sequence number
    const sortedSequence = [...sequence].sort((a, b) => a.sequence_number - b.sequence_number);
    const isSingleOffice = sortedSequence.length === 1;

    return (
      <div className={styles.sequenceList}>
        {sortedSequence.map((step, index) => (
          <div key={index} className={styles.sequenceItem}>
            <div className={styles.sequenceHeader}>
              {!isSingleOffice && (
                <span className={styles.sequenceNumber}>{step.sequence_number}</span>
              )}
              <h5 className={styles.officeName}>{step.office_name}</h5>
            </div>
            <p className={styles.stepPurpose}>{step.purpose}</p>
            <p className={styles.estimatedDuration}>
              Duration: {step.estimated_duration}
            </p>
            {step.is_optional && (
              <span className={styles.optionalBadge}>Optional</span>
            )}
            {step.is_conditional && step.condition && (
              <p className={styles.condition}>
                Condition: {step.condition}
              </p>
            )}
          </div>
        ))}
      </div>
    );
  };

  const renderOfficialWebsites = (websites: OfficialWebsiteLink[]) => {
    if (!websites || websites.length === 0) {
      return <p className={styles.notAvailable}>Information not available</p>;
    }

    return (
      <div className={styles.websitesList}>
        {websites.map((website, index) => (
          <div key={index} className={styles.websiteItem}>
            <a 
              href={website.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className={styles.websiteLink}
            >
              {website.purpose}: {website.url}
            </a>
            {website.description && (
              <p className={styles.websiteDescription}>{website.description}</p>
            )}
          </div>
        ))}
      </div>
    );
  };

  const renderProcessingTimelines = (timelines: ProcessingTimeline[]) => {
    if (!timelines || timelines.length === 0) {
      return <p className={styles.notAvailable}>Information not available</p>;
    }

    return (
      <div className={styles.timelinesList}>
        {timelines.map((timeline, index) => (
          <div key={index} className={styles.timelineItem}>
            <h5 className={styles.processingType}>
              {timeline.processing_type.charAt(0).toUpperCase() + timeline.processing_type.slice(1)} Processing
            </h5>
            <p className={styles.typicalTime}>
              Typical: {timeline.typical_days} {timeline.time_unit}
            </p>
            <p className={styles.timeRange}>
              Range: {timeline.minimum_days}-{timeline.maximum_days} {timeline.time_unit}
            </p>
            {timeline.notes && (
              <p className={styles.timelineNotes}>{timeline.notes}</p>
            )}
            {timeline.factors_affecting_time && timeline.factors_affecting_time.length > 0 && (
              <div className={styles.factors}>
                <strong>Factors affecting time:</strong>
                <ul>
                  {timeline.factors_affecting_time.map((factor, idx) => (
                    <li key={idx}>{factor}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <article className={styles.guideContainer} aria-label="Service Guide">
      <header className={styles.header}>
        <h3 className={styles.serviceName}>{guide.service_name}</h3>
        <p className={styles.description}>{guide.description}</p>
        {guide.last_updated && (
          <p className={styles.lastUpdated}>
            Last updated: {formatDate(guide.last_updated)}
          </p>
        )}
      </header>

      <div className={styles.sectionsContainer}>
        {/* Office Locations Section */}
        <section className={styles.section} aria-labelledby="office-locations-heading">
          <h4 id="office-locations-heading" className={styles.sectionHeader}>
            📍 Office Locations
          </h4>
          <div className={styles.sectionContent}>
            {renderOfficeLocations(guide.office_locations)}
          </div>
        </section>

        {/* Required Documents Section */}
        <section className={styles.section} aria-labelledby="required-documents-heading">
          <h4 id="required-documents-heading" className={styles.sectionHeader}>
            📄 Required Documents
          </h4>
          <div className={styles.sectionContent}>
            {renderRequiredDocuments(guide.required_documents)}
          </div>
        </section>

        {/* Office Visit Sequence Section */}
        <section className={styles.section} aria-labelledby="office-sequence-heading">
          <h4 id="office-sequence-heading" className={styles.sectionHeader}>
            🏢 Office Visit Sequence
          </h4>
          <div className={styles.sectionContent}>
            {renderOfficeVisitSequence(guide.office_visit_sequence)}
          </div>
        </section>

        {/* Official Websites Section */}
        <section className={styles.section} aria-labelledby="official-websites-heading">
          <h4 id="official-websites-heading" className={styles.sectionHeader}>
            🔗 Official Websites
          </h4>
          <div className={styles.sectionContent}>
            {renderOfficialWebsites(guide.official_websites)}
          </div>
        </section>

        {/* Processing Timeline Section */}
        <section className={styles.section} aria-labelledby="processing-timeline-heading">
          <h4 id="processing-timeline-heading" className={styles.sectionHeader}>
            ⏱️ Processing Timeline
          </h4>
          <div className={styles.sectionContent}>
            {renderProcessingTimelines(guide.processing_timelines)}
          </div>
        </section>
      </div>
    </article>
  );
}

export default EnhancedServiceGuideDisplay;