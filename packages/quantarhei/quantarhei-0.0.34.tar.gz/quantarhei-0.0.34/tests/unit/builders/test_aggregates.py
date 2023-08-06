# -*- coding: utf-8 -*-

import unittest
import h5py
import numpy

"""
*******************************************************************************


    Tests of the quantarhei.Aggregate class


*******************************************************************************
"""

from quantarhei import Aggregate
from quantarhei import Molecule
from quantarhei import Mode

from quantarhei import CorrelationFunction
from quantarhei import energy_units
from quantarhei import TimeAxis

from quantarhei.qm import ReducedDensityMatrix


class TestAggregate(unittest.TestCase):
    """Tests for the Manager class
    
    
    """
    
    def setUp(self):
        m1 = Molecule(name="Molecule 1", elenergies=[0.0, 1.0])
        m2 = Molecule(name="Molecule 2", elenergies=[0.0, 1.0])
        
        time = TimeAxis(0.0, 1000, 1.0)
        params = dict(ftype="OverdampedBrownian", reorg=20, cortime=100, T=300)
        with energy_units("1/cm"):
            fc = CorrelationFunction(time, params)
            
        m1.set_transition_environment((0,1), fc)
        m1.position = [0.0, 0.0, 0.0]
        m1.set_dipole(0,1,[10.0, 0.0, 0.0])
        m2.set_transition_environment((0,1), fc)
        m2.position = [10.0, 0.0, 0.0]
        m2.set_dipole(0,1,[10.0, 0.0, 0.0])
        
        self.agg = Aggregate(name="TestAgg", molecules=[m1,m2])
        
        self.agg.set_coupling_by_dipole_dipole()
        
        self.agg.build()
        
        
        m3 = Molecule(name="Molecule 1", elenergies=[0.0, 1.0])
        m4 = Molecule(name="Molecule 2", elenergies=[0.0, 1.0])     
        m3.add_Mode(Mode(0.01))
        m4.add_Mode(Mode(0.01))
        
        mod3 = m3.get_Mode(0)
        mod4 = m4.get_Mode(0)
        
        mod3.set_nmax(0, 4)
        mod3.set_nmax(1, 4)
        mod3.set_HR(1, 0.1)
        mod4.set_nmax(0, 4)
        mod4.set_nmax(1, 4)
        mod4.set_HR(1, 0.3)
        
        self.vagg = Aggregate(molecules=[m3, m4])
        self.vagg.build()


    def test_saving_of_aggregate(self):
        """Testing the saving capability of the Aggregate class
        
        
        """
        use_temporary_file = True
        
        if use_temporary_file: 
            
            drv = "core"
            bcs = False
        
            with h5py.File('tempfile.hdf5', 
                           driver=drv, 
                           backing_store=bcs) as f:
                                             
                self.agg.save(f,report_unsaved=True)
                
                # reread it
                agg = Aggregate()
                agg.load(f)

        else:

            with h5py.File('tempfile.hdf5') as f:                                           
                self.agg.save(f)
            
            with h5py.File('tempfile.hdf5') as f:
                agg = Aggregate()
                agg.load(f)
            
            
        
        self.assertEqual(self.agg.nmono, agg.nmono)
        self.assertEqual(self.agg.mult, agg.mult)
        self.assertEqual(self.agg.sbi_mult, agg.sbi_mult)
        self.assertEqual(self.agg.name, agg.name)
        self.assertEqual(self.agg._has_egcf_matrix, agg._has_egcf_matrix)
        self.assertEqual(self.agg._has_system_bath_interaction,
                         agg._has_system_bath_interaction)
        self.assertEqual(self.agg.coupling_initiated, agg.coupling_initiated)
        self.assertEqual(self.agg._has_relaxation_tensor,
                         agg._has_relaxation_tensor)
        self.assertEqual(self.agg._relaxation_theory, agg._relaxation_theory)
        self.assertEqual(self.agg._built, agg._built)
        self.assertEqual(self.agg.Nel,agg.Nel)
        self.assertEqual(self.agg.Ntot,agg.Ntot)
        numpy.testing.assert_array_equal(self.agg.Nb,agg.Nb)
        for key in agg.mnames.keys():
            self.assertEqual(self.agg.mnames[key],agg.mnames[key])
        numpy.testing.assert_array_equal(self.agg.resonance_coupling, 
                                         agg.resonance_coupling) 
        mnames = ["Molecule 1", "Molecule 2"]
        for k in range(agg.nmono):
            m = agg.monomers[k]
            self.assertIn(m.name, mnames)
            mnames.remove(m.name)
            

    def test_trace_over_vibrations(self):
        """Testing trace over vibrational DOF
        
        """
        
        agg = self.vagg
        
        ham = agg.get_Hamiltonian()
        
        rho = ReducedDensityMatrix(dim=ham.dim)
        rho._data[5, 5] = 1.0
        redr = agg.trace_over_vibrations(rho)
        
        numpy.testing.assert_almost_equal(numpy.trace(redr._data), 1.0,
                                          decimal=7)
        
        N = agg.Nb[0]
        
        rho = ReducedDensityMatrix(dim=ham.dim)
        rho._data[N+5, N+5] = 1.0
        redr = agg.trace_over_vibrations(rho)       

        numpy.testing.assert_almost_equal(numpy.trace(redr._data), 1.0,
                                          decimal=3)


        N = agg.Nb[1]
        
        rho = ReducedDensityMatrix(dim=ham.dim)
        rho._data[N+5, N+5] = 1.0
        redr = agg.trace_over_vibrations(rho)       

        numpy.testing.assert_almost_equal(numpy.trace(redr._data), 1.0,
                                          decimal=2)
        