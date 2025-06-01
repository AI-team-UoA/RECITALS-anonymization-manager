import java.nio.charset.StandardCharsets;
import java.io.File;
import java.io.IOException;

import org.apache.poi.poifs.nio.DataSource;
import org.deidentifier.arx.Data;
import org.deidentifier.arx.DataHandle;
import org.deidentifier.arx.AttributeType.Hierarchy;
import org.deidentifier.arx.criteria.DDisclosurePrivacy;
import org.deidentifier.arx.ARXAnonymizer;
import org.deidentifier.arx.ARXConfiguration;
import org.deidentifier.arx.ARXResult;
import org.deidentifier.arx.AttributeType;
public class DifferentialPrivacyExample {
    public static void main(String[] args) {
        try {
            /* Loads the data. */
            File file = new File("data/data.csv");
            Data data = Data.create(file, StandardCharsets.UTF_8, ',');

            data.getDefinition().setAttributeType("name", AttributeType.IDENTIFYING_ATTRIBUTE);
            data.getDefinition().setAttributeType("last_name", AttributeType.IDENTIFYING_ATTRIBUTE);
            data.getDefinition().setAttributeType("defaulted", AttributeType.SENSITIVE_ATTRIBUTE);
            
            /* Loads the hiearchies. */
            String[] qids = {"age", "balance", "credit_score"};
            for (String qid : qids) {
                 data.getDefinition().setAttributeType(qid, AttributeType.QUASI_IDENTIFYING_ATTRIBUTE);
                 data.getDefinition().setHierarchy(qid, Hierarchy.create(new File("data/"+qid+"_hierarchy.csv"), StandardCharsets.UTF_8, ','));
            }
            
            /* Anonymizes the data. */
            ARXConfiguration config = ARXConfiguration.create();
            config.addPrivacyModel(new DDisclosurePrivacy("defaulted", 0.3));
            ARXAnonymizer anonymizer = new ARXAnonymizer();
            ARXResult res = anonymizer.anonymize(data, config);

            /* Exports the anonymized data. */
            DataHandle out = res.getOutput();
            out.save("anonymized_data/ddisclosure.csv", ',');
        } catch (IOException e) {
            System.out.println(e.getMessage());

        }
    }
}
