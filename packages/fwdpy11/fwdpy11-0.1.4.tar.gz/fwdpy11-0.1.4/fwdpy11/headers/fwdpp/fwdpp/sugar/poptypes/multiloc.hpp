#ifndef __FWDPP_SUGAR_MULTILOC_MULTILOC_HPP__
#define __FWDPP_SUGAR_MULTILOC_MULTILOC_HPP__

#include <type_traits>
#include <vector>
#include <utility>
#include <fwdpp/forward_types.hpp>
#include <fwdpp/sugar/poptypes/tags.hpp>
#include <fwdpp/sugar/poptypes/popbase.hpp>

namespace KTfwd
{
    namespace sugar
    {
        /*!
          \brief Abstraction of what is needed to simulate a multilocus
          simulation using an individual-based sampler from fwdpp.

          All that is missing is the mutation_type and the container types.

          See @ref md_md_sugar for rationale, etc.

          \ingroup sugar
        */
        template <typename mutation_type, typename mcont, typename gcont,
                  typename dipvector, typename mvector, typename ftvector,
                  typename lookup_table_type>
        class multiloc : public popbase<mutation_type, mcont, gcont, dipvector,
                                        mvector, ftvector, lookup_table_type>
        {
          private:
            void
            process_diploid_input()
            {
                std::vector<uint_t> gcounts(this->gametes.size(), 0);
                for (auto &&locus : diploids)
                    {
                        for (auto &&dip : locus)
                            {
                                this->validate_diploid_keys(dip.first,
                                                            dip.second);
                                gcounts[dip.first]++;
                                gcounts[dip.second]++;
                            }
                    }
                this->validate_gamete_counts(gcounts);
            }

          public:
            virtual ~multiloc() = default;
            multiloc(multiloc &&) = default;
            multiloc(const multiloc &) = default;
            multiloc &operator=(multiloc &&) = default;
            multiloc &operator=(const multiloc &) = default;
            //! Dispatch tags for other parts of sugar layer
            using popmodel_t = sugar::MULTILOCPOP_TAG;
            //! Typedef for base class
            using popbase_t = popbase<mutation_type, mcont, gcont, dipvector,
                                      mvector, ftvector, lookup_table_type>;

            static_assert(
                traits::is_multilocus_diploid<
                    typename popbase_t::dipvector_t::value_type>::value,
                "Require that dipvector_t::value_type be a diploid");

            //! Population size
            uint_t N;

            //! Container of individuals
            typename popbase_t::dipvector_t diploids;

            /*! The positional boundaries of each locus/region,
             *  expressed as half-open intervals [min,max).
             *  If nothing is provided, the intervals are assigned
             *  [0,i+1) for all 0 <= i < nloci.
             */
            std::vector<std::pair<double, double>> locus_boundaries;
            /*! Construct with population size, number of loci,
             *  and locus boundaries.  If no locus boundaries
             *  are provided, default values are assigned.
             */
            multiloc(
                const uint_t &__N, const uint_t &__nloci,
                const std::vector<std::pair<double, double>> &locus_boundaries_
                = std::vector<std::pair<double, double>>(),
                typename popbase_t::gamete_t::mutation_container::size_type
                    reserve_size
                = 100)
                : popbase_t(__nloci * __N, reserve_size), N(__N),
                  diploids(__N, typename popbase_t::diploid_t(
                                    __nloci,
                                    typename popbase_t::diploid_t::value_type(
                                        0, 0))),
                  locus_boundaries(locus_boundaries_)
            {
            }

            template <typename diploids_input, typename gametes_input,
                      typename mutations_input>
            explicit multiloc(
                diploids_input &&d, gametes_input &&g, mutations_input &&m,
                const std::vector<std::pair<double, double>> &locus_boundaries_
                = std::vector<std::pair<double, double>>())
                : popbase_t(std::forward<gametes_input>(g),
                            std::forward<mutations_input>(m), 100),
                  N(d.size()), diploids(std::forward<diploids_input>(d)),
                  locus_boundaries(locus_boundaries_)
            {
                this->process_diploid_input();
            }

            bool
            operator==(const multiloc &rhs) const
            {
                return this->diploids == rhs.diploids
                       && this->locus_boundaries == rhs.locus_boundaries
                       && popbase_t::is_equal(rhs);
            }

            //! Empty all containers
            void
            clear()
            {
                diploids.clear();
                locus_boundaries.clear();
                popbase_t::clear_containers();
            }
        };
    }
}

#endif
