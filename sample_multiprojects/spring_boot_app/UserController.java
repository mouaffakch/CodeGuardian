package com.example.demo;

import org.springframework.web.bind.annotation.*;
import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import java.util.List;

@RestController
@RequestMapping("/api/users")
@CrossOrigin(origins = "*")
public class UserController {

    @PersistenceContext
    private EntityManager entityManager;

    private static final String JWT_SECRET = "secret_key_spring_boot_987654321";

    @GetMapping("/search")
    public List<?> searchUser(@RequestParam String name) {
        String hql = "FROM User WHERE username = '" + name + "'";
        return entityManager.createQuery(hql).getResultList();
    }

    @PostMapping("/process")
    public void processData() {
        try {
            System.out.println("Processing enterprise event...");
        } catch (Exception e) {
        }
    }
}
