import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.text.AttributedCharacterIterator.Attribute;
import java.util.HashMap;
import org.deidentifier.arx.Data;
import org.deidentifier.arx.AttributeType;
import org.deidentifier.arx.AttributeType.Hierarchy;
import org.deidentifier.arx.criteria.EqualDistanceTCloseness;
import org.deidentifier.arx.criteria.DistinctLDiversity;
import org.deidentifier.arx.criteria.KAnonymity;
import org.deidentifier.arx.ARXAnonymizer;
import org.deidentifier.arx.ARXConfiguration;
import org.deidentifier.arx.ARXResult;
import org.deidentifier.arx.DataHandle;
import org.deidentifier.arx.DataDefinition;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Set;
import java.util.stream.Stream;

public class JavaArxAdapter {
    /* This holds the data */
    private Data data;
    
    /* Loads the dataset from the given path. */   
    public void loadData(String data_path) {
        try {
            File file = new File(data_path);
            if (!file.exists()) {
                throw new IOException("The dataset could not be located: "+data_path);
            }

            /* It loads the dataset and stores it. */
            this.data = Data.create(data_path, StandardCharsets.UTF_8, ',');
            System.out.println("Data loaded successfully...");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    /* It defines the identifier types. */
    public void defineIdentifiers(ArrayList<String> identifiers) {
        for (String identifier : identifiers) {
            this.data.getDefinition().setAttributeType(identifier, AttributeType.IDENTIFYING_ATTRIBUTE);
        }
        System.out.println("Identifiers defined successfully...");
        System.out.println("Identifiers: "+String.join(", ", identifiers));
    }

    /* It defines the quasi-identifier types. */
    public void defineQuasiIdentifiers(ArrayList<String> quasi_identifiers) {
        for (String quasi_identifier : quasi_identifiers) {
            this.data.getDefinition().setAttributeType(quasi_identifier, AttributeType.QUASI_IDENTIFYING_ATTRIBUTE);
        }
        System.out.println("Quasi-Identifiers defined successfully...");
        System.out.println("Quasi-Identifiers: "+String.join(", ", quasi_identifiers));
    }

    /* It defines the insensitive attributes. */
    public void defineInsensitiveAttributes(ArrayList<String> insensitive_attributes) {
        for (String insensitive_attribute : insensitive_attributes) {
            this.data.getDefinition().setAttributeType(insensitive_attribute, AttributeType.INSENSITIVE_ATTRIBUTE);
        }
        System.out.println("Insensitive attributes defined successfully...");
        System.out.println("Insensitive attributes: "+String.join(", ", insensitive_attributes));
    }

    /* It defines the sensitive attributes. */
    public void defineSensitiveAttributes(ArrayList<String> sensitive_attributes) {
        for (String sensitive_attribute : sensitive_attributes) {
            this.data.getDefinition().setAttributeType(sensitive_attribute, AttributeType.SENSITIVE_ATTRIBUTE);
        }
        System.out.println("Sensitive attributes defined successfully...");
        System.out.println("Sensitive attributes: "+String.join(", ", sensitive_attributes));
    }

    /* Makes the dataset k-anonymous */
    public void makeAnonymous(HashMap<String, Double> parameters, String output_path) {
        try {
            ARXConfiguration config = ARXConfiguration.create();

            /* Checks if k-anonymity should be applied. */
            if (parameters.containsKey("k")) {
                int k = (int)Math.floor(parameters.get("k"));
                config.addPrivacyModel(new KAnonymity(k));
                System.out.println("l-Anonymity will be applied with k="+k);
            } 
            
            /* Checks if l-diversity should be applied. */
            if (parameters.containsKey("l")) {
                int l = (int)Math.floor(parameters.get("l"));
                DataDefinition def = this.data.getDefinition();
                Set<String> sensitive_attributes = def.getSensitiveAttributes();

                for (String sensitive_attribute : sensitive_attributes) {
                    config.addPrivacyModel(new DistinctLDiversity(sensitive_attribute, l));
                }
                System.out.println("l-Diversity will be applied with l="+l+" to the sensitive attributes: "+String.join(", ", sensitive_attributes));
            } 

            /* Checks if t-closeness should be applied. */
            if (parameters.containsKey("t")) {
                double t = parameters.get("t");
                DataDefinition def = this.data.getDefinition();
                Set<String> sensitive_attributes = def.getSensitiveAttributes();

                for (String sensitive_attribute : sensitive_attributes) {
                    config.addPrivacyModel(new EqualDistanceTCloseness(sensitive_attribute, t));
                }
                System.out.println("t-Closeness will be applied with t="+t+" to the sensitive attributes: "+String.join(", ", sensitive_attributes));
            } 

            /* Anonymizes and stores the dataset. */
            ARXAnonymizer anonymizer = new ARXAnonymizer();
            ARXResult res = anonymizer.anonymize(this.data, config);
            DataHandle out = res.getOutput();
            out.save(output_path, ',');
        } catch (IOException e) {
            e.printStackTrace();
        }

    }

    /* It defines the generalization hierarchies. */
    public void defineHierarchies(HashMap<String, String> hierarchies) {
        try {
            for (String quasi_identifier : hierarchies.keySet()) {
                String hierarchy_path = hierarchies.get(quasi_identifier);

                File file = new File(hierarchy_path);

                if (!file.exists()) {
                    throw new IOException("The hierarchy file could not be located: "+hierarchy_path);
                }

                this.data.getDefinition().setHierarchy(quasi_identifier, Hierarchy.create(file, StandardCharsets.UTF_8, ','));
            }
            System.err.println("Hierarchies defined successfully...");
        } catch (IOException e) {
            e.printStackTrace();
        } 
    }
    
    /* Pings the server. */
    public void ping() {
        System.out.println("Ping received");
    }
}