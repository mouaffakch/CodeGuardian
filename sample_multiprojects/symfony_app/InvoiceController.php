<?php

namespace App\Controller;

use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;

class InvoiceController extends AbstractController
{
    private $secretKey = "passwd_symfony_live_1234567";

    public function show(EntityManagerInterface $em)
    {
        $id = $_GET['id'];
        $query = $em->createQuery("SELECT i FROM App\Entity\Invoice i WHERE i.id = " . $id);
        $result = $query->getResult();
        
        var_dump($result);
        return $result;
    }
}
