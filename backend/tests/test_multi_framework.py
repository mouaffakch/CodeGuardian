import pytest
from app.core.static_analyzer import static_analyzer
from app.core.sca_scanner import sca_scanner

def test_spring_boot_detection():
    code = """
@RestController
@CrossOrigin("*")
public class TestController {
    public void query(String name) {
        String hql = "FROM User WHERE name = '" + name;
        em.createQuery(hql);
        try {
            System.out.println("debug");
        } catch (Exception e) {}
    }
}
"""
    res = static_analyzer._analyze_java(code, "TestController.java", {})
    rule_ids = [d["rule_id"] for d in res]
    assert "SPRING-SEC001" in rule_ids
    assert "SPRING-SEC002" in rule_ids
    assert "JAVA-BUG001" in rule_ids
    assert "JAVA-SMELL002" in rule_ids

def test_dotnet_csharp_detection():
    code = """
public class Service {
    public void Run() {
        var cmd = new SqlCommand("SELECT * FROM X WHERE id = " + userInput);
        var f = new BinaryFormatter();
        try {
            var res = task.Result;
        } catch {}
    }
}
"""
    res = static_analyzer._analyze_csharp(code, "Service.cs", {})
    rule_ids = [d["rule_id"] for d in res]
    assert "NET-SEC001" in rule_ids
    assert "NET-SEC002" in rule_ids
    assert "NET-PERF001" in rule_ids
    assert "NET-BUG001" in rule_ids

def test_angular_react_detection():
    code = """
export class Comp {
    init() {
        const x = this.sanitizer.bypassSecurityTrustHtml(raw);
        eval("alert(1)");
    }
}
"""
    res = static_analyzer._analyze_javascript_typescript(code, "Comp.ts", {})
    rule_ids = [d["rule_id"] for d in res]
    assert "ANGULAR-SEC002" in rule_ids
    assert "JS-SEC002" in rule_ids

def test_symfony_php_detection():
    code = """
<?php
class Controller {
    public function index($em) {
        $id = $_GET['id'];
        $em->createQuery("SELECT u FROM User u WHERE u.id = " . $id);
        var_dump($id);
    }
}
"""
    res = static_analyzer._analyze_php(code, "Controller.php", {})
    rule_ids = [d["rule_id"] for d in res]
    assert "PHP-SEC001" in rule_ids
    assert "PHP-SEC002" in rule_ids
    assert "PHP-SMELL001" in rule_ids

def test_ai_pytorch_data_science_detection():
    code = """
import pickle
import torch

def train(model, dataloader):
    weights = torch.load("model.pt", weights_only=False)
    m = pickle.load(open("m.pkl", "rb"))
    loss_acc = 0.0
    for b in dataloader:
        loss = model(b)
        loss_acc += loss
"""
    res = static_analyzer._analyze_python(code, "train.py", {})
    rule_ids = [d["rule_id"] for d in res]
    assert "AI-SEC001" in rule_ids
    assert "AI-SEC002" in rule_ids
    assert "AI-BUG001" in rule_ids

def test_multi_ecosystem_sca(tmp_path):
    pom_file = tmp_path / "pom.xml"
    pom_file.write_text("""<project><dependencies><dependency><artifactId>log4j-core</artifactId><version>2.14.1</version></dependency></dependencies></project>""", encoding="utf-8")
    findings = sca_scanner.scan_directory(str(tmp_path))
    rule_ids = [f["rule_id"] for f in findings]
    assert any("CVE-2021-44228" in r for r in rule_ids)
