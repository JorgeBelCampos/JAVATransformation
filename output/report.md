# Java Migration Analysis Report

## Executive Summary

- **Migration complexity:** HIGH
- **Total code findings:** 242
- **Affected files:** 86
- **Dependency findings:** 12

### Categories

- **General javax Review** (MEDIUM) - 124 findings in 38 files
- **Reflection Encapsulation Risks** (MEDIUM) - 60 findings in 39 files
- **Jakarta Servlet Migration** (HIGH) - 46 findings in 12 files
- **Legacy JSON API** (MEDIUM) - 10 findings in 1 files
- **Internal JDK APIs** (HIGH) - 2 findings in 1 files

### Top Affected Files

- `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLZipHelper.java` - 15 findings
- `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\relprovider\RelationshipTransformService.java` - 14 findings
- `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\XmlHashDocument.java` - 12 findings
- `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugins-manager\src\main\java\es\gob\afirma\standalone\plugins\manager\PluginInfoLoader.java` - 10 findings
- `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\CheckHashDirDialog.java` - 9 findings
- `C:\Users\garet\Desktop\clienteafirma-master\afirma-standalone\afirma-ui-standalone\src\main\java\es\gob\afirma\ui\utils\HelpUtils.java` - 8 findings
- `C:\Users\garet\Desktop\clienteafirma-master\afirma-signature-storage\src\main\java\es\gob\afirma\signfolder\server\proxy\StorageService.java` - 5 findings
- `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\triphase\server\SignatureService.java` - 5 findings
- `C:\Users\garet\Desktop\clienteafirma-master\afirma-miniapplet-report\src\main\java\es\gob\afirma\miniapplet\report\ExtractDataServlet.java` - 5 findings
- `C:\Users\garet\Desktop\clienteafirma-master\afirma-core\src\main\java\es\gob\afirma\core\misc\SecureXmlBuilder.java` - 5 findings

## Migration Strategy

- **Java upgrade required:** YES
- **Jakarta migration:** CONDITIONAL
- **XML impact:** HIGH
- **Internal API risk:** HIGH
- **Estimated effort:** HIGH

### Suggested Plan

1. Upgrade the build configuration and runtime baseline to the target Java version.
2. Review XML-related APIs and add explicit dependencies where JDK-bundled components were removed.
3. Evaluate the target servlet container and decide whether javax.servlet must be migrated to jakarta.servlet.
4. Replace internal JDK API usages with supported public alternatives before final upgrade validation.
5. Run compilation, tests, and smoke validation on the upgraded target runtime.

## Top Fix Candidates

### 1. Plan javax.servlet to jakarta.servlet migration

- **Category:** servlet_migration
- **Impact:** VERY_HIGH
- **Effort:** MEDIUM
- **Affected files:** 12
- **Occurrences:** 46
- **Reason:** Servlet APIs appear in code and are a common blocker for modern Jakarta-based runtimes.
- **Recommendation:** If targeting Tomcat 10+ or Jakarta EE, migrate javax.servlet imports and dependencies to jakarta.servlet.

### 2. Modernize Maven compiler Java level

- **Category:** compiler_config
- **Impact:** VERY_HIGH
- **Effort:** LOW
- **Affected files:** 0
- **Occurrences:** 3
- **Reason:** Old source/target/release values can make builds fail immediately on newer JDKs.
- **Recommendation:** Raise compiler source/target/release and related properties to at least Java 8 before attempting higher-JDK validation.

### 3. Review reflection and encapsulation-sensitive code

- **Category:** reflection_risk
- **Impact:** HIGH
- **Effort:** MEDIUM
- **Affected files:** 39
- **Occurrences:** 60
- **Reason:** Reflection-heavy code can fail under stronger encapsulation in Java 17+.
- **Recommendation:** Review reflective access, setAccessible-style flows, and illegal-access warnings before finalizing Java 17+ migration.

### 4. Upgrade legacy servlet dependencies

- **Category:** dependency_upgrade
- **Impact:** HIGH
- **Effort:** LOW
- **Affected files:** 0
- **Occurrences:** 4
- **Reason:** Old servlet dependencies may block runtime modernization or container upgrades.
- **Recommendation:** Review and replace old servlet artifacts such as servlet-api 2.5 / javax.servlet-api 3.x according to target container.

### 5. Replace internal JDK API usages

- **Category:** internal_api
- **Impact:** HIGH
- **Effort:** LOW
- **Affected files:** 1
- **Occurrences:** 2
- **Reason:** Internal or vendor-specific APIs are risky on newer Java versions and can break at runtime.
- **Recommendation:** Replace com.sun.* / sun.* usages with supported public APIs before final migration validation.

### 6. Review general javax usage

- **Category:** general_javax
- **Impact:** MEDIUM
- **Effort:** HIGH
- **Affected files:** 39
- **Occurrences:** 129
- **Reason:** There is broad javax usage across the codebase, but not all of it requires migration.
- **Recommendation:** Classify javax usages into Java SE, external libs, and Jakarta migration candidates before planning large-scale code changes.

### 7. Review legacy javax.json usage

- **Category:** javax_json_review
- **Impact:** MEDIUM
- **Effort:** LOW
- **Affected files:** 1
- **Occurrences:** 5
- **Reason:** Old javax.json APIs may need explicit dependency management on modern JDKs.
- **Recommendation:** Add explicit javax.json dependency first, then evaluate whether jakarta.json migration is desirable.

## Verification Summary

- **Code findings:** 242 -> 196
- **Dependency findings:** 12 -> 4
- **Servlet code findings:** 46 -> 0
- **Servlet dependency findings:** 4 -> 0

## Build Validation

- **Attempted:** YES
- **Succeeded:** YES
- **Tool:** maven
- **Working directory:** `C:\Users\garet\Desktop\JAVA_Transform\output\fixed_project_20260419_213511`
- **Command:** `C:\maven\apache-maven-3.9.15\bin\mvn.CMD -B -e -Dstyle.color=never --no-transfer-progress -DskipTests compile`
- **Return code:** 0

## Project

- **Path:** `C:\Users\garet\Desktop\clienteafirma-master`
- **Build tool:** `maven`
- **Detected Java version:** `1.7`
- **Target Java version:** `17`

## Compatibility Summary

- Upgrade required: Java 7 → 17
- JAXB and JAX-WS modules were removed from JDK after Java 11
- Strong encapsulation may break reflection-based code

## Dependency Findings

- **Total dependency findings:** 12
- **HIGH:** 5
- **MEDIUM:** 7
- **INFO:** 0

### [HIGH] Legacy javax.servlet dependency detected; may require jakarta migration depending on target runtime

- **Group ID:** `javax.servlet`
- **Artifact ID:** `javax.servlet-api`
- **Version:** `3.0.1`

### [MEDIUM] Legacy javax dependency detected; review whether replacement or explicit dependency management is needed

- **Group ID:** `javax.servlet`
- **Artifact ID:** `javax.servlet-api`
- **Version:** `3.0.1`

### [HIGH] Legacy javax.servlet dependency detected; may require jakarta migration depending on target runtime

- **Group ID:** `javax.servlet`
- **Artifact ID:** `servlet-api`
- **Version:** `2.5`

### [MEDIUM] Legacy javax dependency detected; review whether replacement or explicit dependency management is needed

- **Group ID:** `javax.servlet`
- **Artifact ID:** `servlet-api`
- **Version:** `2.5`

### [MEDIUM] Legacy javax dependency detected; review whether replacement or explicit dependency management is needed

- **Group ID:** `javax.help`
- **Artifact ID:** `javahelp`
- **Version:** `2.0.05`

### [MEDIUM] Legacy javax.json dependency detected; review explicit dependency management or jakarta.json migration

- **Group ID:** `javax.json`
- **Artifact ID:** `javax.json-api`
- **Version:** `1.0`

### [MEDIUM] Legacy javax dependency detected; review whether replacement or explicit dependency management is needed

- **Group ID:** `javax.json`
- **Artifact ID:** `javax.json-api`
- **Version:** `1.0`

### [MEDIUM] Very old dependency version detected; compatibility review recommended

- **Group ID:** `javax.json`
- **Artifact ID:** `javax.json-api`
- **Version:** `1.0`

### [MEDIUM] Legacy javax.json dependency detected; review explicit dependency management or jakarta.json migration

- **Group ID:** `org.glassfish`
- **Artifact ID:** `javax.json`
- **Version:** `1.0.4`

### [HIGH] Legacy Maven compiler configuration detected (source=1.7); newer JDKs may fail to compile

- **Group ID:** `org.apache.maven.plugins`
- **Artifact ID:** `maven-compiler-plugin`
- **Version:** `1.7`

### [HIGH] Legacy Maven compiler configuration detected (target=1.7); newer JDKs may fail to compile

- **Group ID:** `org.apache.maven.plugins`
- **Artifact ID:** `maven-compiler-plugin`
- **Version:** `1.7`

### [HIGH] Legacy Java compiler property detected (jdk.version=1.7); newer JDKs may fail to compile

- **Group ID:** `maven-compiler-plugin`
- **Artifact ID:** `jdk.version`
- **Version:** `1.7`

## Recommendations by Category

### General javax Review

- **Severity:** MEDIUM
- **Findings:** 124
- **Affected files:** 38
- **Recommendation:** Review whether these javax APIs belong to Java SE, legacy Java EE, or external libraries before planning migration changes.

### Reflection Encapsulation Risks

- **Severity:** MEDIUM
- **Findings:** 60
- **Affected files:** 39
- **Recommendation:** Review reflective access patterns because Java 17+ strong encapsulation can require refactoring or --add-opens.

### Jakarta Servlet Migration

- **Severity:** HIGH
- **Findings:** 46
- **Affected files:** 12
- **Recommendation:** If the target runtime is Tomcat 10+ or Jakarta EE, plan a javax.servlet -> jakarta.servlet migration. If staying on Tomcat 9 or equivalent, verify whether keeping javax.servlet is acceptable.

### Legacy JSON API

- **Severity:** MEDIUM
- **Findings:** 10
- **Affected files:** 1
- **Recommendation:** Add explicit javax.json dependency first, then evaluate whether migration to jakarta.json is desirable.

### Internal JDK APIs

- **Severity:** HIGH
- **Findings:** 2
- **Affected files:** 1
- **Recommendation:** Replace internal JDK API usage with supported public alternatives as these are high-risk on newer Java versions.

## Code Findings Summary

- **Total findings:** 242
- **Affected files:** 86
- **HIGH:** 48
- **MEDIUM:** 194
- **INFO:** 0

## Detailed Findings

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-ui-simple-configurator\src\main\java\es\gob\afirma\standalone\configurator\AutofirmaConfigurator.java`
- **Line:** 16
- **Import:** `java.lang.reflect.InvocationTargetException`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-ui-simple-configurator\src\main\java\es\gob\afirma\standalone\configurator\AutofirmaConfigurator.java`
- **Line:** 17
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-ui-core-jse-keystores\src\main\java\es\gob\afirma\ui\core\jse\certificateselection\CertificateUtils.java`
- **Line:** 18
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-ui-core-jse\src\main\java\es\gob\afirma\ui\core\jse\AWTUIManager.java`
- **Line:** 22
- **Import:** `java.lang.reflect.Constructor`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-ui-core-jse\src\main\java\es\gob\afirma\ui\core\jse\AWTUIManager.java`
- **Line:** 23
- **Import:** `java.lang.reflect.InvocationTargetException`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-ui-core-jse\src\main\java\es\gob\afirma\ui\core\jse\AWTUIManager.java`
- **Line:** 24
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-ui-core-jse\src\main\java\es\gob\afirma\ui\core\jse\JSEUIManager.java`
- **Line:** 27
- **Import:** `java.lang.reflect.Constructor`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-ui-core-jse\src\main\java\es\gob\afirma\ui\core\jse\JSEUIManager.java`
- **Line:** 28
- **Import:** `java.lang.reflect.InvocationTargetException`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-ui-core-jse\src\main\java\es\gob\afirma\ui\core\jse\JSEUIManager.java`
- **Line:** 29
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-ui-core-jse\src\main\java\es\gob\afirma\ui\core\jse\JSEUIManager.java`
- **Line:** 35
- **Import:** `javax.accessibility.Accessible`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-ui-core-jse\src\main\java\es\gob\afirma\ui\core\jse\errors\ErrorManagementDialog.java`
- **Line:** 5
- **Import:** `javax.accessibility.Accessible`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-standalone\afirma-ui-standalone\src\main\java\es\gob\afirma\ui\utils\HelpUtils.java`
- **Line:** 34
- **Import:** `javax.help.DefaultHelpBroker`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-standalone\afirma-ui-standalone\src\main\java\es\gob\afirma\ui\utils\HelpUtils.java`
- **Line:** 35
- **Import:** `javax.help.HelpBroker`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-standalone\afirma-ui-standalone\src\main\java\es\gob\afirma\ui\utils\HelpUtils.java`
- **Line:** 36
- **Import:** `javax.help.HelpSet`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-standalone\afirma-ui-standalone\src\main\java\es\gob\afirma\ui\utils\HelpUtils.java`
- **Line:** 37
- **Import:** `javax.help.JHelp`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-standalone\afirma-ui-standalone\src\main\java\es\gob\afirma\ui\utils\HelpUtils.java`
- **Line:** 38
- **Import:** `javax.help.JHelpContentViewer`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-standalone\afirma-ui-standalone\src\main\java\es\gob\afirma\ui\utils\HelpUtils.java`
- **Line:** 39
- **Import:** `javax.help.JHelpNavigator`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-standalone\afirma-ui-standalone\src\main\java\es\gob\afirma\ui\utils\HelpUtils.java`
- **Line:** 40
- **Import:** `javax.help.WindowPresentation`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-standalone\afirma-ui-standalone\src\main\java\es\gob\afirma\ui\utils\HelpUtils.java`
- **Line:** 41
- **Import:** `javax.help.plaf.basic.BasicIndexCellRenderer`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-standalone\afirma-ui-standalone\src\main\java\es\gob\afirma\ui\utils\JAccessibilityFileChooser.java`
- **Line:** 36
- **Import:** `javax.accessibility.AccessibleContext`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-standalone\afirma-ui-standalone\src\main\java\es\gob\afirma\ui\utils\JAccessibilityFileChooserToSave.java`
- **Line:** 33
- **Import:** `javax.accessibility.AccessibleContext`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-standalone\afirma-ui-standalone\src\main\java\es\gob\afirma\ui\visor\ui\EditorFocusManager.java`
- **Line:** 18
- **Import:** `javax.accessibility.AccessibleHyperlink`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-standalone\afirma-ui-standalone\src\main\java\es\gob\afirma\ui\visor\ui\EditorFocusManager.java`
- **Line:** 19
- **Import:** `javax.accessibility.AccessibleHypertext`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugins-manager\src\main\java\es\gob\afirma\standalone\plugins\manager\PluginInfoLoader.java`
- **Line:** 11
- **Import:** `javax.json.Json`

### [MEDIUM] Legacy javax.json API detected; explicit dependency or jakarta.json migration may be needed

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugins-manager\src\main\java\es\gob\afirma\standalone\plugins\manager\PluginInfoLoader.java`
- **Line:** 11
- **Import:** `javax.json.Json`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugins-manager\src\main\java\es\gob\afirma\standalone\plugins\manager\PluginInfoLoader.java`
- **Line:** 12
- **Import:** `javax.json.JsonArray`

### [MEDIUM] Legacy javax.json API detected; explicit dependency or jakarta.json migration may be needed

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugins-manager\src\main\java\es\gob\afirma\standalone\plugins\manager\PluginInfoLoader.java`
- **Line:** 12
- **Import:** `javax.json.JsonArray`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugins-manager\src\main\java\es\gob\afirma\standalone\plugins\manager\PluginInfoLoader.java`
- **Line:** 13
- **Import:** `javax.json.JsonObject`

### [MEDIUM] Legacy javax.json API detected; explicit dependency or jakarta.json migration may be needed

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugins-manager\src\main\java\es\gob\afirma\standalone\plugins\manager\PluginInfoLoader.java`
- **Line:** 13
- **Import:** `javax.json.JsonObject`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugins-manager\src\main\java\es\gob\afirma\standalone\plugins\manager\PluginInfoLoader.java`
- **Line:** 14
- **Import:** `javax.json.JsonReader`

### [MEDIUM] Legacy javax.json API detected; explicit dependency or jakarta.json migration may be needed

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugins-manager\src\main\java\es\gob\afirma\standalone\plugins\manager\PluginInfoLoader.java`
- **Line:** 14
- **Import:** `javax.json.JsonReader`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugins-manager\src\main\java\es\gob\afirma\standalone\plugins\manager\PluginInfoLoader.java`
- **Line:** 15
- **Import:** `javax.json.JsonString`

### [MEDIUM] Legacy javax.json API detected; explicit dependency or jakarta.json migration may be needed

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugins-manager\src\main\java\es\gob\afirma\standalone\plugins\manager\PluginInfoLoader.java`
- **Line:** 15
- **Import:** `javax.json.JsonString`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugins\src\main\java\es\gob\afirma\standalone\plugins\AfirmaPlugin.java`
- **Line:** 3
- **Import:** `java.lang.reflect.Constructor`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugins\src\main\java\es\gob\afirma\standalone\plugins\UIFactory.java`
- **Line:** 7
- **Import:** `java.lang.reflect.Constructor`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugins\src\main\java\es\gob\afirma\standalone\plugins\UIFactory.java`
- **Line:** 8
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\CheckHashDirDialog.java`
- **Line:** 46
- **Import:** `javax.xml.parsers.DocumentBuilder`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\CheckHashDirDialog.java`
- **Line:** 47
- **Import:** `javax.xml.parsers.DocumentBuilderFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\CheckHashDirDialog.java`
- **Line:** 48
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\CheckHashDirDialog.java`
- **Line:** 49
- **Import:** `javax.xml.transform.OutputKeys`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\CheckHashDirDialog.java`
- **Line:** 50
- **Import:** `javax.xml.transform.Transformer`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\CheckHashDirDialog.java`
- **Line:** 51
- **Import:** `javax.xml.transform.TransformerException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\CheckHashDirDialog.java`
- **Line:** 52
- **Import:** `javax.xml.transform.TransformerFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\CheckHashDirDialog.java`
- **Line:** 53
- **Import:** `javax.xml.transform.dom.DOMSource`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\CheckHashDirDialog.java`
- **Line:** 54
- **Import:** `javax.xml.transform.stream.StreamResult`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\XmlHashDocument.java`
- **Line:** 13
- **Import:** `javax.xml.XMLConstants`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\XmlHashDocument.java`
- **Line:** 14
- **Import:** `javax.xml.parsers.DocumentBuilder`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\XmlHashDocument.java`
- **Line:** 15
- **Import:** `javax.xml.parsers.DocumentBuilderFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\XmlHashDocument.java`
- **Line:** 16
- **Import:** `javax.xml.transform.OutputKeys`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\XmlHashDocument.java`
- **Line:** 17
- **Import:** `javax.xml.transform.Transformer`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\XmlHashDocument.java`
- **Line:** 18
- **Import:** `javax.xml.transform.TransformerFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\XmlHashDocument.java`
- **Line:** 19
- **Import:** `javax.xml.transform.dom.DOMSource`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\XmlHashDocument.java`
- **Line:** 20
- **Import:** `javax.xml.transform.stream.StreamResult`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\XmlHashDocument.java`
- **Line:** 21
- **Import:** `javax.xml.transform.stream.StreamSource`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\XmlHashDocument.java`
- **Line:** 22
- **Import:** `javax.xml.validation.Schema`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\XmlHashDocument.java`
- **Line:** 23
- **Import:** `javax.xml.validation.SchemaFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple-plugin-hash\src\main\java\es\gob\afirma\plugin\hash\XmlHashDocument.java`
- **Line:** 24
- **Import:** `javax.xml.validation.Validator`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple\src\main\java\es\gob\afirma\standalone\DesktopUtil.java`
- **Line:** 21
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple\src\main\java\es\gob\afirma\standalone\SimpleAfirma.java`
- **Line:** 33
- **Import:** `java.lang.reflect.InvocationTargetException`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple\src\main\java\es\gob\afirma\standalone\SimpleAfirma.java`
- **Line:** 34
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple\src\main\java\es\gob\afirma\standalone\SimpleAfirma.java`
- **Line:** 50
- **Import:** `javax.smartcardio.CardTerminal`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple\src\main\java\es\gob\afirma\standalone\protocol\ProtocolInvocationLauncher.java`
- **Line:** 14
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple\src\main\java\es\gob\afirma\standalone\ui\CommonWaitDialog.java`
- **Line:** 17
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple\src\main\java\es\gob\afirma\standalone\ui\EditorFocusManager.java`
- **Line:** 25
- **Import:** `javax.accessibility.AccessibleHyperlink`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple\src\main\java\es\gob\afirma\standalone\ui\EditorFocusManager.java`
- **Line:** 26
- **Import:** `javax.accessibility.AccessibleHypertext`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple\src\main\java\es\gob\afirma\standalone\ui\MainMenu.java`
- **Line:** 17
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple\src\main\java\es\gob\afirma\standalone\ui\OSXHandler.java`
- **Line:** 23
- **Import:** `java.lang.reflect.InvocationHandler`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple\src\main\java\es\gob\afirma\standalone\ui\OSXHandler.java`
- **Line:** 24
- **Import:** `java.lang.reflect.InvocationTargetException`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple\src\main\java\es\gob\afirma\standalone\ui\OSXHandler.java`
- **Line:** 25
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple\src\main\java\es\gob\afirma\standalone\ui\OSXHandler.java`
- **Line:** 26
- **Import:** `java.lang.reflect.Proxy`

### [HIGH] Internal JDK APIs are risky and may break on newer Java versions

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple\src\main\java\es\gob\afirma\standalone\ui\restoreconfig\RestoreConfigWindows.java`
- **Line:** 33
- **Import:** `com.sun.jna.platform.win32.Advapi32Util`

### [HIGH] Internal JDK APIs are risky and may break on newer Java versions

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-simple\src\main\java\es\gob\afirma\standalone\ui\restoreconfig\RestoreConfigWindows.java`
- **Line:** 34
- **Import:** `com.sun.jna.platform.win32.WinReg`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-signature-storage\src\main\java\es\gob\afirma\signfolder\server\proxy\StorageService.java`
- **Line:** 23
- **Import:** `javax.servlet.ServletException`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-signature-storage\src\main\java\es\gob\afirma\signfolder\server\proxy\StorageService.java`
- **Line:** 24
- **Import:** `javax.servlet.ServletInputStream`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-signature-storage\src\main\java\es\gob\afirma\signfolder\server\proxy\StorageService.java`
- **Line:** 25
- **Import:** `javax.servlet.http.HttpServlet`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-signature-storage\src\main\java\es\gob\afirma\signfolder\server\proxy\StorageService.java`
- **Line:** 26
- **Import:** `javax.servlet.http.HttpServletRequest`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-signature-storage\src\main\java\es\gob\afirma\signfolder\server\proxy\StorageService.java`
- **Line:** 27
- **Import:** `javax.servlet.http.HttpServletResponse`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-signature-retriever\src\main\java\es\gob\afirma\signfolder\server\proxy\RetrieveService.java`
- **Line:** 20
- **Import:** `javax.servlet.ServletException`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-signature-retriever\src\main\java\es\gob\afirma\signfolder\server\proxy\RetrieveService.java`
- **Line:** 21
- **Import:** `javax.servlet.http.HttpServlet`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-signature-retriever\src\main\java\es\gob\afirma\signfolder\server\proxy\RetrieveService.java`
- **Line:** 22
- **Import:** `javax.servlet.http.HttpServletRequest`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-signature-retriever\src\main\java\es\gob\afirma\signfolder\server\proxy\RetrieveService.java`
- **Line:** 23
- **Import:** `javax.servlet.http.HttpServletResponse`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer-core\src\main\java\es\gob\afirma\triphase\signer\processors\XAdESTriPhasePreProcessor.java`
- **Line:** 25
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer-core\src\main\java\es\gob\afirma\triphase\signer\processors\XAdESTriPhaseSignerUtil.java`
- **Line:** 21
- **Import:** `javax.xml.parsers.DocumentBuilderFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer-core\src\main\java\es\gob\afirma\triphase\signer\processors\XAdESTriPhaseSignerUtil.java`
- **Line:** 22
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer-core\src\main\java\es\gob\afirma\triphase\signer\xades\XAdESTriPhaseSignerServerSide.java`
- **Line:** 39
- **Import:** `javax.xml.parsers.DocumentBuilderFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer-core\src\main\java\es\gob\afirma\triphase\signer\xades\XAdESTriPhaseSignerServerSide.java`
- **Line:** 40
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\test\java\es\gob\afirma\signers\batch\TestSignBatch.java`
- **Line:** 4
- **Import:** `java.lang.reflect.InvocationTargetException`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\triphase\server\SignatureService.java`
- **Line:** 16
- **Import:** `java.lang.reflect.Constructor`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\triphase\server\SignatureService.java`
- **Line:** 17
- **Import:** `java.lang.reflect.Method`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\triphase\server\SignatureService.java`
- **Line:** 39
- **Import:** `javax.servlet.http.HttpServlet`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\triphase\server\SignatureService.java`
- **Line:** 40
- **Import:** `javax.servlet.http.HttpServletRequest`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\triphase\server\SignatureService.java`
- **Line:** 41
- **Import:** `javax.servlet.http.HttpServletResponse`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\triphase\server\VersionService.java`
- **Line:** 6
- **Import:** `javax.servlet.ServletException`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\triphase\server\VersionService.java`
- **Line:** 7
- **Import:** `javax.servlet.http.HttpServlet`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\triphase\server\VersionService.java`
- **Line:** 8
- **Import:** `javax.servlet.http.HttpServletRequest`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\triphase\server\VersionService.java`
- **Line:** 9
- **Import:** `javax.servlet.http.HttpServletResponse`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\json\DocumentCacheFactory.java`
- **Line:** 4
- **Import:** `java.lang.reflect.Constructor`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\json\JSONSignBatch.java`
- **Line:** 14
- **Import:** `java.lang.reflect.Constructor`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\server\BatchPostsigner.java`
- **Line:** 21
- **Import:** `javax.servlet.ServletException`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\server\BatchPostsigner.java`
- **Line:** 22
- **Import:** `javax.servlet.http.HttpServlet`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\server\BatchPostsigner.java`
- **Line:** 23
- **Import:** `javax.servlet.http.HttpServletRequest`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\server\BatchPostsigner.java`
- **Line:** 24
- **Import:** `javax.servlet.http.HttpServletResponse`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\server\BatchPresigner.java`
- **Line:** 21
- **Import:** `javax.servlet.ServletException`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\server\BatchPresigner.java`
- **Line:** 22
- **Import:** `javax.servlet.http.HttpServlet`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\server\BatchPresigner.java`
- **Line:** 23
- **Import:** `javax.servlet.http.HttpServletRequest`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\server\BatchPresigner.java`
- **Line:** 24
- **Import:** `javax.servlet.http.HttpServletResponse`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\server\JSONBatchPostsigner.java`
- **Line:** 21
- **Import:** `javax.servlet.ServletException`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\server\JSONBatchPostsigner.java`
- **Line:** 22
- **Import:** `javax.servlet.http.HttpServlet`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\server\JSONBatchPostsigner.java`
- **Line:** 23
- **Import:** `javax.servlet.http.HttpServletRequest`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\server\JSONBatchPostsigner.java`
- **Line:** 24
- **Import:** `javax.servlet.http.HttpServletResponse`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\server\JSONBatchPresigner.java`
- **Line:** 19
- **Import:** `javax.servlet.ServletException`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\server\JSONBatchPresigner.java`
- **Line:** 20
- **Import:** `javax.servlet.http.HttpServlet`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\server\JSONBatchPresigner.java`
- **Line:** 21
- **Import:** `javax.servlet.http.HttpServletRequest`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\server\JSONBatchPresigner.java`
- **Line:** 22
- **Import:** `javax.servlet.http.HttpServletResponse`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\server\RequestParameters.java`
- **Line:** 17
- **Import:** `javax.servlet.http.HttpServletRequest`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\xml\SignBatch.java`
- **Line:** 22
- **Import:** `javax.xml.parsers.SAXParser`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-triphase-signer\src\main\java\es\gob\afirma\signers\batch\xml\SignBatch.java`
- **Line:** 23
- **Import:** `javax.xml.parsers.SAXParserFactory`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-simple-webstart\src\main\java\es\gob\afirma\server\webstart\AutoFirmaJnlpService.java`
- **Line:** 16
- **Import:** `javax.servlet.ServletException`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-simple-webstart\src\main\java\es\gob\afirma\server\webstart\AutoFirmaJnlpService.java`
- **Line:** 17
- **Import:** `javax.servlet.http.HttpServlet`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-simple-webstart\src\main\java\es\gob\afirma\server\webstart\AutoFirmaJnlpService.java`
- **Line:** 18
- **Import:** `javax.servlet.http.HttpServletRequest`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-server-simple-webstart\src\main\java\es\gob\afirma\server\webstart\AutoFirmaJnlpService.java`
- **Line:** 19
- **Import:** `javax.servlet.http.HttpServletResponse`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-miniapplet-store-testdata\src\main\java\es\gob\afirma\webtests\TestStorer.java`
- **Line:** 8
- **Import:** `javax.servlet.annotation.WebServlet`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-miniapplet-store-testdata\src\main\java\es\gob\afirma\webtests\TestStorer.java`
- **Line:** 9
- **Import:** `javax.servlet.http.HttpServlet`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-miniapplet-store-testdata\src\main\java\es\gob\afirma\webtests\TestStorer.java`
- **Line:** 10
- **Import:** `javax.servlet.http.HttpServletRequest`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-miniapplet-store-testdata\src\main\java\es\gob\afirma\webtests\TestStorer.java`
- **Line:** 11
- **Import:** `javax.servlet.http.HttpServletResponse`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-miniapplet-report\src\main\java\es\gob\afirma\miniapplet\report\ExtractDataServlet.java`
- **Line:** 6
- **Import:** `javax.servlet.ServletOutputStream`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-miniapplet-report\src\main\java\es\gob\afirma\miniapplet\report\ExtractDataServlet.java`
- **Line:** 7
- **Import:** `javax.servlet.annotation.WebServlet`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-miniapplet-report\src\main\java\es\gob\afirma\miniapplet\report\ExtractDataServlet.java`
- **Line:** 8
- **Import:** `javax.servlet.http.HttpServlet`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-miniapplet-report\src\main\java\es\gob\afirma\miniapplet\report\ExtractDataServlet.java`
- **Line:** 9
- **Import:** `javax.servlet.http.HttpServletRequest`

### [HIGH] Likely javax -> jakarta migration candidate

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-miniapplet-report\src\main\java\es\gob\afirma\miniapplet\report\ExtractDataServlet.java`
- **Line:** 10
- **Import:** `javax.servlet.http.HttpServletResponse`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-keystores-mozilla\src\test\java\es\gob\afirma\keystores\mozilla\SimpleTest.java`
- **Line:** 5
- **Import:** `java.lang.reflect.InvocationTargetException`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-keystores-mozilla\src\main\java\es\gob\afirma\keystores\mozilla\MozillaKeyStoreUtilities.java`
- **Line:** 22
- **Import:** `java.lang.reflect.InvocationTargetException`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-keystores-mozilla\src\main\java\es\gob\afirma\keystores\mozilla\MozillaKeyStoreUtilities.java`
- **Line:** 23
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-keystores-jmulticard-ui\src\main\java\es\gob\afirma\keystores\jmulticard\ui\DnieCacheCallbackHandler.java`
- **Line:** 3
- **Import:** `java.lang.reflect.InvocationTargetException`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-keystores-jmulticard-ui\src\main\java\es\gob\afirma\keystores\jmulticard\ui\DnieCacheCallbackHandler.java`
- **Line:** 4
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-keystores-jmulticard-ui\src\main\java\es\gob\afirma\keystores\jmulticard\ui\DnieCallbackHandler.java`
- **Line:** 3
- **Import:** `java.lang.reflect.InvocationTargetException`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-keystores-jmulticard-ui\src\main\java\es\gob\afirma\keystores\jmulticard\ui\DnieCallbackHandler.java`
- **Line:** 4
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-keystores-capiaddressbook\src\main\java\sun\security\mscapi\KeyStoreAddressBook.java`
- **Line:** 31
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xmlsignature\src\main\java\es\gob\afirma\signers\xmldsig\AOXMLDSigSigner.java`
- **Line:** 51
- **Import:** `javax.xml.parsers.DocumentBuilderFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xmlsignature\src\main\java\es\gob\afirma\signers\xmldsig\AOXMLDSigSigner.java`
- **Line:** 52
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xmlsignature\src\main\java\es\gob\afirma\signers\xmldsig\AOXMLDSigSigner.java`
- **Line:** 53
- **Import:** `javax.xml.transform.OutputKeys`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xmlsignature\src\main\java\es\gob\afirma\signers\xmldsig\CustomUriDereferencer.java`
- **Line:** 14
- **Import:** `java.lang.reflect.Constructor`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xmlsignature\src\main\java\es\gob\afirma\signers\xmldsig\CustomUriDereferencer.java`
- **Line:** 15
- **Import:** `java.lang.reflect.Field`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xmlsignature\src\main\java\es\gob\afirma\signers\xmldsig\CustomUriDereferencer.java`
- **Line:** 16
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xmlsignature\src\main\java\es\gob\afirma\signers\xmldsig\CustomUriDereferencer.java`
- **Line:** 25
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xades\src\main\java\es\gob\afirma\signers\xades\AOFacturaESigner.java`
- **Line:** 20
- **Import:** `javax.xml.parsers.DocumentBuilder`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xades\src\main\java\es\gob\afirma\signers\xades\AOXAdESSigner.java`
- **Line:** 23
- **Import:** `javax.xml.parsers.DocumentBuilder`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xades\src\main\java\es\gob\afirma\signers\xades\AOXAdESSigner.java`
- **Line:** 24
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xades\src\main\java\es\gob\afirma\signers\xades\XAdESSigner.java`
- **Line:** 45
- **Import:** `javax.xml.parsers.DocumentBuilder`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xades\src\main\java\es\gob\afirma\signers\xades\XAdESTspUtil.java`
- **Line:** 16
- **Import:** `javax.xml.datatype.DatatypeFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xades\src\main\java\es\gob\afirma\signers\xades\XAdESTspUtil.java`
- **Line:** 17
- **Import:** `javax.xml.parsers.DocumentBuilderFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xades\src\main\java\es\gob\afirma\signers\xades\XAdESTspUtil.java`
- **Line:** 18
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xades\src\main\java\es\gob\afirma\signers\xades\XAdESTspUtil.java`
- **Line:** 19
- **Import:** `javax.xml.transform.OutputKeys`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xades\src\main\java\es\gob\afirma\signers\xades\XAdESUtil.java`
- **Line:** 36
- **Import:** `javax.xml.transform.OutputKeys`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xades\src\main\java\es\gob\afirma\signers\xades\XAdESUtil.java`
- **Line:** 37
- **Import:** `javax.xml.xpath.XPathConstants`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xades\src\main\java\es\gob\afirma\signers\xades\XAdESUtil.java`
- **Line:** 38
- **Import:** `javax.xml.xpath.XPathExpressionException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-xades\src\main\java\es\gob\afirma\signers\xades\XAdESUtil.java`
- **Line:** 39
- **Import:** `javax.xml.xpath.XPathFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-pdf\src\test\java\es\gob\afirma\test\pades\TestMetadata.java`
- **Line:** 18
- **Import:** `javax.xml.parsers.DocumentBuilder`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-pdf\src\main\java\es\gob\afirma\signers\pades\PdfPreProcessor.java`
- **Line:** 14
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-pdf\src\main\java\es\gob\afirma\signers\pades\PdfSignResult.java`
- **Line:** 19
- **Import:** `javax.xml.datatype.DatatypeFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-pdf\src\main\java\es\gob\afirma\signers\pades\PdfSignResult.java`
- **Line:** 20
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-pdf\src\main\java\es\gob\afirma\signers\pades\PdfTimestamper.java`
- **Line:** 15
- **Import:** `java.lang.reflect.InvocationTargetException`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-pdf\src\main\java\es\gob\afirma\signers\pades\PdfTimestamper.java`
- **Line:** 16
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-pdf\src\main\java\es\gob\afirma\signers\pades\XmpHelper.java`
- **Line:** 27
- **Import:** `javax.xml.parsers.DocumentBuilder`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-pdf\src\main\java\es\gob\afirma\signers\pades\XmpHelper.java`
- **Line:** 28
- **Import:** `javax.xml.parsers.DocumentBuilderFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-pdf\src\main\java\es\gob\afirma\signers\pades\XmpHelper.java`
- **Line:** 29
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\ContentTypeManager.java`
- **Line:** 18
- **Import:** `javax.xml.parsers.DocumentBuilder`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\ContentTypeManager.java`
- **Line:** 19
- **Import:** `javax.xml.parsers.DocumentBuilderFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\ContentTypeManager.java`
- **Line:** 20
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLPackageObjectHelper.java`
- **Line:** 38
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLUtil.java`
- **Line:** 21
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLXAdESSigner.java`
- **Line:** 34
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLZipHelper.java`
- **Line:** 25
- **Import:** `javax.xml.XMLConstants`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLZipHelper.java`
- **Line:** 26
- **Import:** `javax.xml.namespace.NamespaceContext`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLZipHelper.java`
- **Line:** 27
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLZipHelper.java`
- **Line:** 28
- **Import:** `javax.xml.transform.OutputKeys`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLZipHelper.java`
- **Line:** 29
- **Import:** `javax.xml.transform.Result`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLZipHelper.java`
- **Line:** 30
- **Import:** `javax.xml.transform.Source`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLZipHelper.java`
- **Line:** 31
- **Import:** `javax.xml.transform.Transformer`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLZipHelper.java`
- **Line:** 32
- **Import:** `javax.xml.transform.TransformerException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLZipHelper.java`
- **Line:** 33
- **Import:** `javax.xml.transform.dom.DOMSource`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLZipHelper.java`
- **Line:** 34
- **Import:** `javax.xml.transform.stream.StreamResult`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLZipHelper.java`
- **Line:** 35
- **Import:** `javax.xml.xpath.XPath`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLZipHelper.java`
- **Line:** 36
- **Import:** `javax.xml.xpath.XPathConstants`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLZipHelper.java`
- **Line:** 37
- **Import:** `javax.xml.xpath.XPathExpression`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLZipHelper.java`
- **Line:** 38
- **Import:** `javax.xml.xpath.XPathExpressionException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\OOXMLZipHelper.java`
- **Line:** 39
- **Import:** `javax.xml.xpath.XPathFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\RelationshipsParser.java`
- **Line:** 17
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\relprovider\RelationshipTransformService.java`
- **Line:** 55
- **Import:** `javax.xml.XMLConstants`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\relprovider\RelationshipTransformService.java`
- **Line:** 64
- **Import:** `javax.xml.namespace.NamespaceContext`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\relprovider\RelationshipTransformService.java`
- **Line:** 65
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\relprovider\RelationshipTransformService.java`
- **Line:** 66
- **Import:** `javax.xml.transform.OutputKeys`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\relprovider\RelationshipTransformService.java`
- **Line:** 67
- **Import:** `javax.xml.transform.Result`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\relprovider\RelationshipTransformService.java`
- **Line:** 68
- **Import:** `javax.xml.transform.Source`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\relprovider\RelationshipTransformService.java`
- **Line:** 69
- **Import:** `javax.xml.transform.Transformer`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\relprovider\RelationshipTransformService.java`
- **Line:** 70
- **Import:** `javax.xml.transform.TransformerException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\relprovider\RelationshipTransformService.java`
- **Line:** 71
- **Import:** `javax.xml.transform.dom.DOMSource`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\relprovider\RelationshipTransformService.java`
- **Line:** 72
- **Import:** `javax.xml.transform.stream.StreamResult`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\relprovider\RelationshipTransformService.java`
- **Line:** 73
- **Import:** `javax.xml.xpath.XPath`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\relprovider\RelationshipTransformService.java`
- **Line:** 74
- **Import:** `javax.xml.xpath.XPathConstants`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\relprovider\RelationshipTransformService.java`
- **Line:** 75
- **Import:** `javax.xml.xpath.XPathExpression`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-ooxml\src\main\java\es\gob\afirma\signers\ooxml\relprovider\RelationshipTransformService.java`
- **Line:** 76
- **Import:** `javax.xml.xpath.XPathFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-odf\src\main\java\es\gob\afirma\signers\odf\AOODFSigner.java`
- **Line:** 58
- **Import:** `javax.xml.transform.OutputKeys`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-odf\src\main\java\es\gob\afirma\signers\odf\AOODFSigner.java`
- **Line:** 59
- **Import:** `javax.xml.transform.Transformer`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-odf\src\main\java\es\gob\afirma\signers\odf\AOODFSigner.java`
- **Line:** 60
- **Import:** `javax.xml.transform.dom.DOMSource`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-odf\src\main\java\es\gob\afirma\signers\odf\AOODFSigner.java`
- **Line:** 61
- **Import:** `javax.xml.transform.stream.StreamResult`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-core-xml\src\main\java\es\gob\afirma\signers\xml\Utils.java`
- **Line:** 43
- **Import:** `javax.xml.parsers.DocumentBuilder`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-core-xml\src\main\java\es\gob\afirma\signers\xml\Utils.java`
- **Line:** 44
- **Import:** `javax.xml.parsers.DocumentBuilderFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-core-xml\src\main\java\es\gob\afirma\signers\xml\Utils.java`
- **Line:** 45
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-core-xml\src\main\java\es\gob\afirma\signers\xml\Utils.java`
- **Line:** 46
- **Import:** `javax.xml.transform.OutputKeys`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-core-xml\src\main\java\es\gob\afirma\signers\xml\XmlDSigProviderHelper.java`
- **Line:** 3
- **Import:** `java.lang.reflect.InvocationTargetException`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-core-xml\src\main\java\es\gob\afirma\signers\xml\dereference\CustomUriDereferencer.java`
- **Line:** 14
- **Import:** `java.lang.reflect.Constructor`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-core-xml\src\main\java\es\gob\afirma\signers\xml\dereference\CustomUriDereferencer.java`
- **Line:** 15
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-core-xml\src\main\java\es\gob\afirma\signers\xml\dereference\CustomUriDereferencer.java`
- **Line:** 24
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-core-xml\src\main\java\es\gob\afirma\signers\xml\dereference\XMLSignatureInput.java`
- **Line:** 32
- **Import:** `javax.xml.parsers.DocumentBuilder`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-core-xml\src\main\java\es\gob\afirma\signers\xml\dereference\XMLSignatureInput.java`
- **Line:** 33
- **Import:** `javax.xml.parsers.DocumentBuilderFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-core-xml\src\main\java\es\gob\afirma\signers\xml\dereference\XMLSignatureInput.java`
- **Line:** 34
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-core-pkcs7-tsp\src\main\java\es\gob\afirma\signers\tsp\pkcs7\CMSTimestamper.java`
- **Line:** 18
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-cms-enveloper\src\test\java\es\gob\afirma\envelopers\cms\TestTemd.java`
- **Line:** 5
- **Import:** `java.lang.reflect.Field`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-cades\src\test\java\es\gob\afirma\test\cades\MiniTestDNI.java`
- **Line:** 14
- **Import:** `java.lang.reflect.Constructor`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-cades\src\main\java\es\gob\afirma\signers\cades\AOCAdESSigner.java`
- **Line:** 13
- **Import:** `java.lang.reflect.Constructor`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-cades\src\main\java\es\gob\afirma\signers\cades\AOCAdESSigner.java`
- **Line:** 14
- **Import:** `java.lang.reflect.InvocationTargetException`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-cades\src\main\java\es\gob\afirma\signers\cades\AOCAdESSigner.java`
- **Line:** 15
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-crypto-cades\src\main\java\es\gob\afirma\signers\cades\asic\AOCAdESASiCSSigner.java`
- **Line:** 13
- **Import:** `java.lang.reflect.InvocationTargetException`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-core-keystores\src\test\java\es\gob\afirma\test\keystores\TestDnie.java`
- **Line:** 15
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-core-keystores\src\test\java\es\gob\afirma\test\keystores\TestPkcs11.java`
- **Line:** 5
- **Import:** `java.lang.reflect.Constructor`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-core-keystores\src\main\java\es\gob\afirma\keystores\AOKeyStoreManagerHelperFullJava.java`
- **Line:** 13
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-core-keystores\src\main\java\es\gob\afirma\keystores\AOKeyStoreManagerHelperPkcs11.java`
- **Line:** 18
- **Import:** `java.lang.reflect.InvocationTargetException`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-core-keystores\src\main\java\es\gob\afirma\keystores\AOKeyStoreManagerHelperPkcs11.java`
- **Line:** 19
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-core-keystores\src\main\java\es\gob\afirma\keystores\CAPIKeyStoreManager.java`
- **Line:** 13
- **Import:** `java.lang.reflect.Field`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-core\src\main\java\es\gob\afirma\core\misc\AOFileUtils.java`
- **Line:** 33
- **Import:** `javax.xml.parsers.SAXParser`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-core\src\main\java\es\gob\afirma\core\misc\MimeHelper.java`
- **Line:** 14
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-core\src\main\java\es\gob\afirma\core\misc\SecureXmlBuilder.java`
- **Line:** 6
- **Import:** `javax.xml.parsers.DocumentBuilder`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-core\src\main\java\es\gob\afirma\core\misc\SecureXmlBuilder.java`
- **Line:** 7
- **Import:** `javax.xml.parsers.DocumentBuilderFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-core\src\main\java\es\gob\afirma\core\misc\SecureXmlBuilder.java`
- **Line:** 8
- **Import:** `javax.xml.parsers.ParserConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-core\src\main\java\es\gob\afirma\core\misc\SecureXmlBuilder.java`
- **Line:** 9
- **Import:** `javax.xml.parsers.SAXParser`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-core\src\main\java\es\gob\afirma\core\misc\SecureXmlBuilder.java`
- **Line:** 10
- **Import:** `javax.xml.parsers.SAXParserFactory`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-core\src\main\java\es\gob\afirma\core\misc\SecureXmlTransformer.java`
- **Line:** 6
- **Import:** `javax.xml.transform.Transformer`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-core\src\main\java\es\gob\afirma\core\misc\SecureXmlTransformer.java`
- **Line:** 7
- **Import:** `javax.xml.transform.TransformerConfigurationException`

### [MEDIUM] javax.* usage detected; review whether migration is required

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-core\src\main\java\es\gob\afirma\core\misc\SecureXmlTransformer.java`
- **Line:** 8
- **Import:** `javax.xml.transform.TransformerFactory`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-core\src\main\java\es\gob\afirma\core\signers\ExtraParamsProcessor.java`
- **Line:** 15
- **Import:** `java.lang.reflect.Method`

### [MEDIUM] Reflection or encapsulation-sensitive API detected; Java 17+ may require refactoring or --add-opens

- **File:** `C:\Users\garet\Desktop\clienteafirma-master\afirma-core\src\main\java\es\gob\afirma\core\misc\http\SSLErrorProcessor.java`
- **Line:** 4
- **Import:** `java.lang.reflect.Method`
